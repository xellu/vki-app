export type InboxMessage = {
    title: string,
    body: string,
    
    createdAt: number,
    read: boolean
}

export type Profile = {
    _id: string,

    email: string,
    password?: string,

    name: string,
    group: string,

    settings: {
        timetable: null | string,
        langId: string, //en_us/ru_ru

    }

    inbox: InboxMessage[]
}
