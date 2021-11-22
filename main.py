from overloaded_harbor import Overloaded_Harbor

ans = 0
N = 100    #Number of simulations
T = 10000  #Duration of each simulation in hours
for i in range (0,N):
    test = Overloaded_Harbor()
    test.run(T)
    ans += test.answer
ans = ans/N
print(ans)
#Answer varied according tu the method used to generate the random distribution.
#Runing 100 simulations, each one with a time period of 10^4 hours and using distributions generated  by:
#scipy -> 14.98 hours
#box muller -> 15.44 hours