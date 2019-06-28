#!/usr/bin/env python3


def numberToString(numString):
    newString = ""
    for i in range(len(numString)):
        try:
            num = int(numString[i])
            if num == 0:
                newString += "_Zero"
            elif num == 1:
                newString += "_One"
            elif num == 2:
                newString += "_Two"
            elif num == 3:
                newString += "_Three"
            elif num == 4:
                newString += "_Four"
            elif num == 5:
                newString += "_Five"
            elif num == 6:
                newString += "_Six"
            elif num == 7:
                newString += "_Seven"
            elif num == 8:
                newString += "_Eight"
            elif num == 9:
                newString += "_Nine"
        except ValueError:
            newString += numString[i]
    return newString
