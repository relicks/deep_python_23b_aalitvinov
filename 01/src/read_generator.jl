using Base.Iterators: Filter

"""
    grepiter(iterable, wordfilter)

Iteratively searches for a list of words in each element of `iterable`.

Iterates over the strings in the iterator and returns only
those strings where at least one of the words for searching was found.
The search is performed with full word matching, case insensitive.
"""
function grepiter(iterable, wordfilter)
    wordset = Set(lowercase.(wordfilter))

    return Iterators.filter(
        line -> !isempty((line |> split .|> lowercase |> Set) ∩ wordset),
        iterable,
    )
end

"""
    grepfile(file::AbstractString, wordfilter)::Filter

Iteratively searches for a list of words in each line of the file.

Iterates over the lines in the file and returns only
those lines where at least one of the words for searching was found.
The search is performed with full word matching, case insensitive.
"""
function grepfile(file::AbstractString, wordfilter)
    @assert isfile(file)

    return grepiter(eachline(file), wordfilter)
end

# Example usage
test_path = "tests/data/calabaria.txt"
grepfile(test_path, ["и"]) |> collect


lines = ["Hello world", "This is a test", "Another line with hello", "what is this?"]
wordfilter = ["hello", "test"]

collect(grepiter(lines, wordfilter))

io = open(test_path, "r")
