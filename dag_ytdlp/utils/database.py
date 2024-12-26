def get_database_url(dialect, driver, username, passwd, host, port, database):
    if driver is None or driver == "":
        driver_prefix = ""
        driver = ""
    else:
        driver_prefix = "+"

    if passwd is None or passwd == "":
        passwd_prefix = ""
        passwd = ""
    else:
        passwd_prefix = ":"

    url = f"{dialect}{driver_prefix}{driver}://{username}{passwd_prefix}{passwd}@{host}:{port}/{database}"
    return url
