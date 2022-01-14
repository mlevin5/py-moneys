# py-moneys

graph.py is an implementation of the transaction optimization algorithms discussed in [this paper](https://pure.tue.nl/ws/portalfiles/portal/2062204/623903.pdf). 
improvements can be made towards time complexity and storage usage, though some choices were made in favor of readability and simplicity.
it could also use a lot more test cases.

moneys.py is the start to a collection of tools to keep track of reciepts, transactions between people, and the pot of money between them.
work still needs to be done here, especially in the case of integrating the concept of a shared pot of excess money with the transaction optimization logic from graph.py

for now, all of this is in python just because it's quick and easy to get running, but i would like to convert this into a kotlin project at some point.

