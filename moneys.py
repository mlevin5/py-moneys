import enum
import datetime
  
# TODO: add functionality for the POT
class Comrade(enum.Enum):
	pot = 1   # the pot is where everyone owns the money equally -> for house emergencies and joint profits.
	megan = 2
	theia = 3
	other = 4  

class MoneyActionType(enum.Enum):
	expensed = 1 # expensed a purchase to the moneytracker
	paid = 2 # paid what they owe to the moneytracker

class Category(enum.Enum):
	rent = 1
	mortgage = 2
	sharedExpense = 3
	sharedProfit = 4

	def moneyActionsAllowed():
		actionsAllowedByCategory = {
		Category.rent: [MoneyActionType.gave], 
		Category.mortgage: [MoneyActionType.took],
		Category.sharedExpense: [MoneyActionType.took],
		Category.sharedProfit: [MoneyActionType.gave]
		}
		return actionsAllowedByCategory[self]

# things that the user inputs
class MoneyAction():
	def __init__(self, moneyActionType, comradeTakingAction, comradesInvolved, amount, category, description, dateReported):
		self.moneyActionType = moneyActionType
		self.comradeTakingAction = comradeTakingAction
		self.comradesInvolved = comradesInvolved
		self.amount = amount
		self.category = category
		self.description = description
		self.dateReported = dateReported

# things user inputs + additional information from backend
class Receipt:
	def __init__(self, moneyAction, dateAdded): 
		self.history = []

class MoneyTracker:
	def __init__(self): 
		# record keeping
		self.paidReciepts = []
		self.activeReciepts = []

		# dictionary of dictionary
		# e.g. totalsOwedByComrade[megan][theia] = total that megan owes theia
		self.totalsOwedByComrades = {}


	def initializeComradesInTotals(self, comradeTakingAction, comrade):
		if not comradeTakingAction in self.totalsOwedByComrades:
			self.totalsOwedByComrades[comradeTakingAction] = {}
		if not comrade in self.totalsOwedByComrades:
			self.totalsOwedByComrades[comrade] = {}
		if not comradeTakingAction in self.totalsOwedByComrades[comrade]:
			self.totalsOwedByComrades[comrade][comradeTakingAction] = 0
		if not comrade in self.totalsOwedByComrades[comradeTakingAction]:
			self.totalsOwedByComrades[comradeTakingAction][comrade] = 0


	def fileMoneyActionAsReciept(self, moneyAction):
		receipt = Receipt(moneyAction, datetime.datetime.now())
		self.activeReciepts.append(receipt);

		for comrade in moneyAction.comradesInvolved:
			percentage = 1.0/len(moneyAction.comradesInvolved)
	
			paymentSign = -1.0 if moneyAction.moneyActionType == MoneyActionType.expensed else 1.0

			self.initializeComradesInTotals(moneyAction.comradeTakingAction, comrade)

			#comrade taking action owes comrade
			self.totalsOwedByComrades[moneyAction.comradeTakingAction][comrade] += paymentSign * moneyAction.amount * percentage

			#comrade owes comrade taking action
			self.totalsOwedByComrades[comrade][moneyAction.comradeTakingAction] -= paymentSign * moneyAction.amount * percentage

	def previewSettlement(self):
		for comradeWhoOwes, info in self.totalsOwedByComrades.items():
			for comradeWhoRecieves, amount in info.items():
				if amount > 0:
					print(comradeWhoOwes.name + " owes " + comradeWhoRecieves.name + " " + "$" + str(amount))

	def ownerPays(self, owner, amount):
		s = ""
		totalOfTotals = 0;
		for owner, total in self.totals:

			s += owner + " owns " + total + " of the pot. \n"

			totalOfTotals += total

		s += "Total in the pot: " + totalOfTotals + "\n"

		print(s)


	#def getHistory():


def main():
	mt = MoneyTracker()
	mt.fileMoneyActionAsReciept(MoneyAction(MoneyActionType.expensed, Comrade.megan, [Comrade.megan, Comrade.theia, Comrade.other], 33, Category.sharedExpense, "sewing machine", datetime.datetime.now()))
	mt.fileMoneyActionAsReciept(MoneyAction(MoneyActionType.expensed, Comrade.theia, [Comrade.megan, Comrade.theia, Comrade.other], 18, Category.sharedExpense, "sewing machin2e", datetime.datetime.now()))
	mt.fileMoneyActionAsReciept(MoneyAction(MoneyActionType.expensed, Comrade.other, [Comrade.megan, Comrade.theia, Comrade.other], 21, Category.sharedExpense, "sewing machi3ne", datetime.datetime.now()))

	mt.previewSettlement()

main()








#theia owes other $1.0
#theia owes megan $5.0
#other owes megan $4.0

#theia owes megan $6.0
#other owes megan $3.0

#other owes theia  1
#other owes megan 16
#theia owes megan 

#megan theia other 
#9     -6    -3








