import re
import asyncio
import httpx
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from random_header_generator import HeaderGenerator

from .models.Order import Order
from .models.Grade import GradeEntry, SubjectGrades, Year

from nautica.services.logger import LogManager
from nautica.services.database.xeldb import XelDB
from src.lib.Language import Messages

NSU_BASE = "https://cab.nsu.ru"

logger = LogManager("Lib.NsuAPI")
_header_gen = HeaderGenerator()

YearsDB = XelDB("Cache-NsuAPI", primary_key="key")


class NsuAPIError(Exception):
    pass


class NsuAPI:
    def __init__(self, cookies):
        headers = _header_gen(country="ru")

        self._session = requests.Session()
        self._session.headers.update(headers)
        self._session.cookies = cookies

        self._cookies = dict(cookies)
        self._headers = dict(headers)

        self._years: dict[str, Year] | None = None  # in-memory layer on top of XelDB

    #AUTH------------------------------------------------------------------

    @staticmethod
    async def login(email: str, password: str) -> tuple[dict, None] | tuple[None, str]:
        """
        Authenticate against cab.nsu.ru.

        Returns:
            (cookies, None)  on success
            (None, error)    on failure
        """
        async with httpx.AsyncClient(headers=_header_gen(country="ru"), follow_redirects=True, timeout=30.0) as client:
            r = await client.get(f"{NSU_BASE}/user/sign-in/auth?authclient=nsu")
            if not r.is_success:
                return None, "Failed to load login form"

            form = BeautifulSoup(r.text, "html.parser").find("form", {"id": "kc-form-login"})
            if not form:
                return None, "Login form not found"

            r2 = await client.post(str(form["action"]), data={"username": email, "password": password})

            if not r2.cookies.get("PHPSESSID"):
                return None, Messages.NSUAPI_INVALID_LOGIN.value

            return dict(r2.cookies), None

    def get_profile(self) -> tuple[str, None]:
        """
        Retrieves legal name and class/group from cab.nsu.ru
        
        Returns
            (name, None) None on failure
            (group, None)
        """
        
        session = requests.Session()
        session.headers.update(_header_gen(country="ru"))

        r = self._session.get(f"{NSU_BASE}/user/profile")
        if not r.ok:
            raise NsuAPIError("Unable to fetch profile")
        
        #find name paragraph
        bs = BeautifulSoup(r.text, "html.parser")
        name_p = bs.find("p", class_="name")
        group_p = bs.find_all("p")
        
        name = name_p.get_text().strip() if name_p else None
        group = None
        
        for p in group_p:
            if "Группа:" in p.get_text():
                group = p.get_text()

        if group:
            group = group.strip().replace("Группа: В", "")

        return name, group


    #ORDERS------------------------------------------------------------------
    
    def get_orders(self) -> list[Order]:
        r = self._session.get(f"{NSU_BASE}/vkistudent/orders")
        if not r.ok:
            raise NsuAPIError("Unable to fetch orders")

        orders = []
        table = BeautifulSoup(r.text, "html.parser").find("table", class_="table-nsu")
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                title = cells[1].find("b").text.strip()
                body = re.sub(r'\s+', ' ', cells[1].contents[-1].replace('\n', ' ')).strip()
                orders.append(Order(title=title, body=body))

        return orders

    #GRADES------------------------------------------------------------------
    
    async def _load_years(self, client: httpx.AsyncClient) -> dict[str, Year]:
        """Return year/semester mapping, using in-memory -> XelDB -> network."""
        if self._years is not None:
            return self._years

        cached = YearsDB.getByKey("global")
        if cached:
            self._years = {
                yid: Year(name=y["name"], semesters=y["semesters"])
                for yid, y in cached["years"].items()
            }
            return self._years

        r = await client.get(f"{NSU_BASE}/vkistudent/journal")
        if not r.is_success:
            raise NsuAPIError(f"Failed to fetch journal (HTTP {r.status_code})")

        #find year ids
        w0 = BeautifulSoup(r.text, "html.parser").find("select", id="w0")
        if not w0:
            raise NsuAPIError("Year selector not found on journal page")

        #create years and assign semesters
        years: dict[str, Year] = {}
        semester = 1
        for opt in w0.find_all("option"):
            year_id = opt.attrs.get("value")
            if year_id:
                years[year_id] = Year(name=opt.get_text(strip=True), semesters=[semester, semester + 1])
                semester += 2

        years_data = {yid: {"name": y.name, "semesters": y.semesters} for yid, y in years.items()}
        if cached:
            YearsDB.setByKey("global", "years", years_data)
        else:
            YearsDB.create(key="global", years=years_data)

        self._years = years
        return self._years

    def invalidate_years_cache(self):
        """Force a re-fetch of the year/semester mapping on the next call."""
        self._years = None
        YearsDB.removeByKey("global")

    async def get_latest_semester(self) -> int:
        """Return the highest semester number available for this user."""
        async with httpx.AsyncClient(cookies=self._cookies, headers=self._headers, follow_redirects=True, timeout=30.0) as client:
            years = await self._load_years(client)
        latest = max(s for y in years.values() for s in y.semesters)

        today = datetime.today()
        if today.month == 1 and today.day < 31:
            return latest - 1
        return latest

    async def get_grades(self, semester: int) -> list[SubjectGrades]:
        """Return all subject grades for the given semester number."""
        async with httpx.AsyncClient(cookies=self._cookies, headers=self._headers, follow_redirects=True, timeout=30.0) as client:
            years = await self._load_years(client)

            #get year id for a provided semester
            year_id = next(
                (yid for yid, year in years.items() if semester in year.semesters),
                None,
            )
            if not year_id:
                raise NsuAPIError(f"Semester {semester} not found")

            r = await client.get(
                f"{NSU_BASE}/vkistudent/journal",
                params={"StatementSearch[year]": year_id, "semester": semester},
            )
            if not r.is_success:
                raise NsuAPIError("Unable to fetch subject list")

            tab = BeautifulSoup(r.text, "html.parser").find("div", id=f"tab-{semester}")
            if not tab:
                raise NsuAPIError(f"Tab for semester {semester} not found in response")

            urls = [a["href"] for a in tab.find_all("a") if a.get("href")]
            return list(await asyncio.gather(*[self._get_subject_grades(client, url) for url in urls]))

    async def _get_subject_grades(self, client: httpx.AsyncClient, url: str) -> SubjectGrades:
        r = await client.get(f"{NSU_BASE}{url}")
        if not r.is_success:
            raise NsuAPIError(f"Unable to fetch subject page: {url}")

        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find("li", class_="breadcrumb-item active").text.split(",", 1)[-1].strip()

        #idk i half-pasted this
        entries = []
        for row in soup.find("table", class_="table-diary").find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 7:
                grade_str = cells[3].text.strip()
                entries.append(GradeEntry(
                    date=cells[0].text.strip(),
                    type=cells[1].text.strip() or None,
                    was_absent=cells[2].text.strip() == "Н",
                    grade=grade_str,
                    value=self._parse_grade_value(grade_str),
                    description=cells[4].text.strip(),
                ))

        return SubjectGrades(name=name, url=url, grades=entries)

    @staticmethod
    def _parse_grade_value(grade: str) -> int:
        digits = "".join(c for c in grade if c.isdigit()) #if there's some shit like 4-
        return int(digits) if digits else 0
