**Question**

1. Write a code (using either Python/C#) that reads a strings from command line and finds out the longest substring in it that doesn't contain any duplicate characters.
If there are more than one substrings in equal length that satisfy the condition, returning any of these substrings would be a valid answer.

2. Also please comment on the space and time complexity of your solution.


**Input Format**

- The first line contains a single string, **input:**.

**Output Format**
- The output should be displayed after **output:**, including **length:**

Expected input and output:
```
> solution.exe (for C#) 
> python3 solution.py (for Python)
input: ABBCDDEFGHII
output: DEFGHI length: 6

> solution.exe (for C#) 
> python3 solution.py (for Python)
input: AABBCCD
output: AB length: 2
output: BC length: 2
output: CD length: 2
<any of the above 3 would be accepted>

> solution.exe (for C#) 
> python3 solution.py (for Python)
input: ABCD
output: ABCD length: 4
