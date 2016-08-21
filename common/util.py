# For library
def convertSteamAccount(id):
    if len(str(id)) == 17:
        temp = str(id)
        return int(temp[3:]) - 61197960265728
    else:
        return '765' + str(int(x) + 61197960265728)