import { writable, type Writable } from "svelte/store";
import { temp } from "$lib/scripts/Temp";

import type { Profile } from "$lib/models/User";

type AuthStateType = {
    loggedIn: boolean,
    loading: boolean,
    error?: string,
    rateLimited?: boolean,
    auto?: string //remote, local
}

export type { Profile, AuthStateType };



const Account: Writable<null | Profile> = writable<null | Profile>(null);
const AuthState: Writable<AuthStateType> = writable<AuthStateType>({loggedIn: false, loading: true});
const AuthModalState: Writable<boolean> = writable(false);

export { Account, AuthState, AuthModalState };


async function Authenticate(): Promise<{state: AuthStateType, account?: Profile}> {
    AuthState.set({loggedIn: false, loading: true});

    const r = await fetch(`/api/v1/auth/me`, {
        method: "POST",
    })

    //if the request failed
    if (!r.ok) {
        const res = {
            loggedIn: false,
            loading: false,
            error: "Session expired"
        }
        AuthState.set(res);
        return {state: res};
    }

    const account = await r.json() as Profile;

    if (!account) {
        const res = {
            loggedIn: false,
            loading: false,
            error: "Unable to get account data"
        }
        AuthState.set(res);
        return {state: res};
    }

    Account.set(account);
    localStorage.setItem("account.data", JSON.stringify(account));
    localStorage.setItem("account.expire", (Date.now() + 1000 * 60).toString()); //update account data every minute

    const res = {
        loggedIn: true,
        loading: false,
        auto: "remote"
    }
    AuthState.set(res);
    return {state: res, account: account};
}

async function AutoAuthenticate(): Promise<{state: AuthStateType, account?: Profile}> {
    AuthState.set({loggedIn: false, loading: true});

    //check if the session cookie exists
    const cookies = document.cookie.split("; ");
    const session = cookies.find(c => c.startsWith("session="))?.split("=")[1];
    if (!session) {
        const res = {loggedIn: false, loading: false};

        AuthState.set(res);
        return {state: res};
    }

    let localExpire = localStorage.getItem("account.expire");
    if (!localExpire || parseInt(localExpire) < Date.now() && parseInt(localExpire) !== -1) { //load remote content
        const res = await Authenticate();
        if (!res.state.loggedIn) { localStorage.setItem("account.expire", "-1"); } //disable auto auth

        AuthState.set(res.state);
        return res;
    }

    if (localExpire && parseInt(localExpire) === -1) { //disable auto auth
        const res = {loggedIn: false, loading: false};

        AuthState.set(res);
        return {state: res};
    }

    if (localExpire && parseInt(localExpire) > Date.now()) { //auth successful - load local content
        const res = {loggedIn: true, loading: false, auto: "local"}
        const acc = JSON.parse(localStorage.getItem("account.data") as string) as Profile;

        Account.set(acc);
        AuthState.set(res);
        return {state: res, account: acc };
    }

    //auth with the server
    const res: {state: AuthStateType, account?: Profile} = await Authenticate();

    return res;
}


async function LogIn(email: string, password: string): Promise<AuthStateType> {
    if (!email || !password) {
        const res = {loggedIn: false, loading: false, error: "Missing fields"}
        
        AuthState.set(res);
        return res
    }

    try {
        AuthState.set({loggedIn: false, loading: true});

        const r = await fetch(`/api/v1/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({email, password})
        })

        //if the request failed
        if (!r.ok) {
            const e = await r.json();
            const res = {
                loggedIn: false,
                loading: false,
                error: e.error || "unknownError",
                rateLimited: r.status === 429
            }

            AuthState.set(res);
            return res;
        }

        const data = await r.json();
        const session = data?.session;

        if (!session) {
            const res = {
                loggedIn: false,
                loading: false,
                error: "cantGetSession"
            }
            AuthState.set(res);
            return res;
        }

        document.cookie = `session=${session}; path=/`;

        const res = await Authenticate();
        
        AuthState.set(res.state);
        return res.state;
    } catch (e) {
        const res = {loggedIn: false, loading: false, error: `${e}`}
        AuthState.set(res);
        return res;
    }
}

async function LogOut(): Promise<AuthStateType> {
    AuthState.set({loggedIn: false, loading: true});

    try {
        let localExpire = localStorage.getItem("account.expire");
        if (localExpire && parseInt(localExpire) > Date.now()) { //this means the account is still valid
            const r = await fetch(`/api/v1/auth/logout`, {
                method: "POST"
            })
        }

        localStorage.removeItem("account.data");
        localStorage.removeItem("account.expire");
        document.cookie = "session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        
        const res = {loggedIn: false, loading: false}
        AuthState.set(res);
        Account.set(null);

        return res;

    } catch (e) {
        const res = {loggedIn: false, loading: false, error: `${e}`}
        AuthState.set(res);
        return res;
    }
}

export {
    LogIn,
    LogOut,
    Authenticate,
    AutoAuthenticate
}