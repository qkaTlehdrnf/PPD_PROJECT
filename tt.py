#프로그래머스 여행경로
from collections import defaultdict as defdict
def solution(tickets):
    flights = defdict(list)
    for i in tickets:
        flights[i[0]] += [i[1]]
    for i in flights:
        flights[i].sort()
    depart = "ICN"
    route = [tuple(["ICN"])]
    cur_flights = flights
    while len(route) < len(tickets) + 1:
        arrivals = cur_flights[depart]
        route.append(tuple(arrivals))
        try:
            depart=cur_flights[depart].pop(0)
        except IndexError:
            print(cur_flights)
            exit()
    answer = []
    for i in route:
        answer.append(i[0])
    return answer
solution([["ICN", "SFO"], ["ICN", "ATL"], ["SFO", "ATL"], ["ATL", "ICN"], ["ATL", "SFO"]])
solution([["ICN", "AOO"], ["AOO", "BOO"], ["BOO", "COO"], ["COO", "DOO"], ["DOO", "EOO"], ["EOO", "DOO"], ["DOO", "COO"], ["COO", "BOO"], ["BOO", "AOO"]])

