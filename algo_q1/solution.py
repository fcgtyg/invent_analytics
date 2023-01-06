def find_longest_substring(input_:str) -> str:
    """
    Finds the longest substring in the input string that doesn't contain any duplicate characters.
    
    This function has time and space complexity O(n), as it traverses the input string once and stores the longest and current substrings, which have a maximum length of n.
    
    Args:
        input_string (str): The input string to search for the longest substring.
        
    Returns:
        str: The longest substring of the input string that doesn't contain any duplicate characters.
        
    Example:
        find_longest_substring("AABBCCD") -> "CD"
    """
    longest = ""
    current = ""

    for c in input_:
        if c not in current:
            current += c
        else:
            longest = max(longest, current)
            current = c
    
    return max(longest, current)

if __name__ == "__main__":
    #input_ = input("input: ")
    input_ = "AABBCCD"
    output = find_longest_substring(input_)
    print(f"Output: {output} length: {len(output)}")