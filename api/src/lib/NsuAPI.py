import re
import requests
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

YearsDB = XelDB("NsuAPI-Cache1", primary_key="key")


class NsuAPIError(Exception):
    pass


class NsuAPI:
    def __init__(self, cookies):
        self._session = requests.Session()
        self._session.headers.update(_header_gen(country="ru"))
        self._session.cookies = cookies

        self._years: dict[str, Year] | None = None  # in-memory layer on top of XelDB

    #AUTH------------------------------------------------------------------

    @staticmethod
    def login(email: str, password: str) -> tuple[requests.cookies.RequestsCookieJar, None] | tuple[None, str]:
        """
        Authenticate against cab.nsu.ru.

        Returns:
            (cookies, None)  on success
            (None, error)    on failure
        """
        session = requests.Session()
        session.headers.update(_header_gen(country="ru"))

        r = session.get(f"{NSU_BASE}/user/sign-in/auth?authclient=nsu")
        if not r.ok:
            return None, "Failed to load login form"

        form = BeautifulSoup(r.text, "html.parser").find("form", {"id": "kc-form-login"})
        if not form:
            return None, "Login form not found"

        r2 = session.post(form["action"], data={"username": email, "password": password})
        session.close()

        # if "Invalid username or password" in r2.text:
        #     return None, "Invalid credentials"
        if not r2.cookies.get("PHPSESSID"):
            return None, Messages.NSUAPI_INVALID_LOGIN.value

        return r2.cookies, None

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
    
    def _load_years(self) -> dict[str, Year]:
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

        r = self._session.get(f"{NSU_BASE}/vkistudent/journal")
        if not r.ok:
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

    def get_grades(self, semester: int) -> list[SubjectGrades]:
        """Return all subject grades for the given semester number."""
        years = self._load_years()

        #get year id for a provided semester
        year_id = next(
            (yid for yid, year in years.items() if semester in year.semesters),
            None,
        )
        if not year_id:
            raise NsuAPIError(f"Semester {semester} not found")

        r = self._session.get(
            f"{NSU_BASE}/vkistudent/journal",
            params={"StatementSearch[year]": year_id, "semester": semester},
        )
        if not r.ok:
            raise NsuAPIError("Unable to fetch subject list")

        tab = BeautifulSoup(r.text, "html.parser").find("div", id=f"tab-{semester}")
        if not tab:
            raise NsuAPIError(f"Tab for semester {semester} not found in response")

        urls = [a["href"] for a in tab.find_all("a") if a.get("href")]
        return [self._get_subject_grades(url) for url in urls]

    def _get_subject_grades(self, url: str) -> SubjectGrades:
        r = self._session.get(f"{NSU_BASE}{url}")
        if not r.ok:
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
