export function getCookie(c_name) {
    if (!document.cookie) {
        return "";
    }

    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();
        if (!trimmedCookie.startsWith(`${c_name}=`)) {
            continue;
        }

        const value = trimmedCookie.substring(c_name.length + 1);
        return decodeURIComponent(value);
    }

    return "";
}