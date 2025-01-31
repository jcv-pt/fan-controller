class Stack:
    """
    A stack with a maximum size that supports adding integers and calculating the average.
    """

    def __init__(self, maxSize: int):
        """
        Initializes the stack with a maximum size.

        Parameters:
            maxSize (int): The maximum number of elements the stack can hold.
        """
        self.__stack = []
        self.__maxSize = maxSize

    def push(self, num):
        """
        Pushes a number onto the stack. If the stack exceeds max_size, removes the oldest element.

        Parameters:
            num (int): The number to add to the stack.
        """
        self.__stack.append(num)
        if len(self.__stack) > self.__maxSize:
            self.__stack.pop(0)  # Remove the oldest element (FIFO behavior)

    def getAverage(self):
        """
        Returns the average of the elements in the stack.

        Returns:
            float: The average of the stack elements. Returns 0 if the stack is empty.
        """
        return sum(self.__stack) / len(self.__stack) if self.__stack else 0

    def getRepeated(self):
        """
        Counts the number of repeated values in the stack.

        Returns:
            int: The number of repeated values in the stack.
        """
        from collections import Counter
        counter = Counter(self.__stack)
        # Count how many values occur more than once
        return sum(count > 1 for count in counter.values())

    def getCount(self):
        """
        Returns stack count
        :return:
        """
        return len(self.__stack)

    def getRepeatedAsPer(self):
        """
        Gets the number of elements in the stack as percentage.
        :return:
        """
        return int((self.getRepeated() * 100) / self.__maxSize)

    def isFull(self):
        """
        Gets the number of elements in the stack as percentage.
        :return:
        """
        return self.getCount() == self.__maxSize