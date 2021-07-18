import sys, os, time, datetime, asyncio, aiohttp

f = open('/dev/null', 'w')
sys.stderr = f

def moveCursor(x, y):
    sys.stdout.write("\033[" + str(y) + ";" + str(x) + "H")
    sys.stdout.flush()

#         | dark | bright |
# --------+------+--------+
# black   |   0  |    8   |
# red     |   1  |    9   |
# green   |   2  |   10   |
# yellow  |   3  |   11   |
# blue    |   4  |   12   |
# magenta |   5  |   13   |
# cyan    |   6  |   14   |
# white   |   7  |   15   |

def writeText(x, y, text, fcolor=None, bcolor=None):
    if fcolor == None:
        pass
    elif type(fcolor) != int:
        raise TypeError("writeText()'s 'fcolor' attribute must be an Int or None.")
    elif (fcolor > -1) and (fcolor < 8):
        sys.stdout.write("\033[" + str(fcolor+30) + "m")
    elif (fcolor > 7) and (fcolor < 16):
        sys.stdout.write("\033[" + str(fcolor+22) + ";1m")
    else:
        raise ValueError("writeText()'s 'fcolor' attribute must be between 0 and 15.")
    if bcolor == None:
        pass
    elif type(bcolor) != int:
        raise TypeError("writeText()'s 'bcolor' attribute must be an Int or None.")
    elif (bcolor > -1) and (bcolor < 8):
        sys.stdout.write("\033[" + str(bcolor+40) + "m")
    else:
        raise ValueError("writeText()'s 'bcolor' attribute must be between 0 and 7.")
    moveCursor(x, y)
    sys.stdout.write(text)
    sys.stdout.write("\u001b[0m")
    sys.stdout.flush()

async def writeTextA(x, y, text, fcolor=None, bcolor=None):
    if fcolor == None:
        pass
    elif type(fcolor) != int:
        raise TypeError("writeText()'s 'fcolor' attribute must be an Int or None.")
    elif (fcolor > -1) and (fcolor < 8):
        sys.stdout.write("\033[" + str(fcolor+30) + "m")
    elif (fcolor > 7) and (fcolor < 16):
        sys.stdout.write("\033[" + str(fcolor+22) + ";1m")
    else:
        raise ValueError("writeText()'s 'fcolor' attribute must be between 0 and 15.")
    if bcolor == None:
        pass
    elif type(bcolor) != int:
        raise TypeError("writeText()'s 'bcolor' attribute must be an Int or None.")
    elif (bcolor > -1) and (bcolor < 8):
        sys.stdout.write("\033[" + str(bcolor+40) + "m")
    else:
        raise ValueError("writeText()'s 'bcolor' attribute must be between 0 and 7.")
    moveCursor(x, y)
    sys.stdout.write(text)
    sys.stdout.write("\u001b[0m")
    sys.stdout.flush()

def bell():
    sys.stdout.write("\007")
    sys.stdout.flush()

def clearLine(line):
    moveCursor(1, line)
    sys.stdout.write(" "*120)
    sys.stdout.flush()

async def clock():
    while True:
        await writeTextA(113, 1, datetime.datetime.now().strftime("%I:%M %p"), 12, 7)
        await asyncio.sleep(1)

version = "0.6"
view_count = 0
timeouts = 0

os.system("clear")
writeText(1, 1, "rcViewbot Ver. " + version, 0, 3)
writeText(1, 2, "Total Views: ", 0, 7)
writeText(14, 2, "0", 15, 4)

async def inc_count(_type):
    global view_count
    global timeouts
    if _type: view_count += 1
    else: timeouts += 1
    await writeTextA(14, 2, str(view_count).rjust(7), 15, 4)
    await writeTextA(21, 2, "+", 0, 7)
    await writeTextA(22, 2, str(timeouts).rjust(5), 15, 1)
    

async def inner_loop(session, id, b):
    a = await session.request("GET", "https://tbgforums.com/forums/viewtopic.php?id="+str(id))
    #print(a.status, b)
    await writeTextA(4, 4+b, str(a.status), 0, 2)
    

async def middle_loop(session, id, b, timeout):
    global reps
    global touts
    await writeTextA(1, 4+b, str(b).rjust(2))
    #print(b, "start")
    while True:
        try:
            await asyncio.wait_for(inner_loop(session, id, b), timeout)
            reps[b] += 1
            await writeTextA(8, 4+b, str(reps[b]).rjust(7), 6)
            await inc_count(True)
            await asyncio.sleep(0.25)
        except KeyboardInterrupt:
            sys.exit()
        except (asyncio.TimeoutError, asyncio.futures.TimeoutError, TimeoutError):
            touts[b] += 1
            await writeTextA(16, 4+b, str(touts[b]).rjust(4), 1)
            await inc_count(False)
            await writeTextA(4, 4+b, "out", 0, 1)
        except (ConnectionResetError, aiohttp.client_exceptions.ClientConnectionError):
            await writeTextA(4, 4+b, "cce", 0, 5)
        except Exception:
            raise
            #print("timeout", b)

async def outer_loop(id, count):
    #connector = aiohttp.TCPConnector(force_close=True)
    #async with aiohttp.ClientSession(connector=connector) as session:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(count):
            tasks.append(middle_loop(session, id, i, 1))
        tasks.append(clock())
        await asyncio.gather(*tasks)
    #await asyncio.gather(asyncio.create_task(inner_loop(id, 1)), asyncio.create_task(inner_loop(id, 2)), asyncio.create_task(inner_loop(id, 3)), asyncio.create_task(inner_loop(id, 4)))

writeText(1, 3, "Thread ID ")
tID = int(input("> "))
writeText(1, 4, "Concurrent View Count (max 16) ")
vCount = min(int(input("> ")), 16)
reps = [0]*vCount
touts = [0]*vCount
clearLine(3)
clearLine(4)

writeText(115, 2, str(tID).rjust(6), 15, 7)

asyncio.run(outer_loop(tID, vCount))