import string
import requests
import json
import sys


def get_filtered_freq_list(corpus, word_length, nonexistent_letters, existent_letters, global_exclude):
    """Get a sequence of letters in the order of frequency of appearance in the corpus after applying filters.
    :param corpus: list of words
    :param word_length: int
    :param nonexistent_letters: list of letters
    :param existent_letters: list of {letter:idx} based on guess string
    :param global_exclude: list of letters
    :return: string
    """
    existent_letters_list = [item["letter"] for item in existent_letters]
    letter_to_frequency = {letter: 0 for letter in set(string.ascii_uppercase)-set(existent_letters_list) -
                           set(nonexistent_letters) - set(global_exclude)}
    for word in corpus:
        continue_flag = False

        # Filter for specific word length
        if len(word) != word_length and word_length != 10000:
            continue

        # Filter for wrongly guessed letter in current word
        for nonexistent_letter in nonexistent_letters:
            if nonexistent_letter in word:
                continue_flag = True
                break

        # Filter for already guessed letter in current word
        for existent_letter in existent_letters:
            if existent_letter["letter"] != word[existent_letter['position']]:
                continue_flag = True
                break

        if continue_flag:
            continue
        for character in word:
            try:
                letter_to_frequency[character.upper()] += 1
            except KeyError:
                continue

    # Sort the resulting frequency mapping and convert to a string in the order of frequency
    sorted_by_value = sorted(letter_to_frequency.items(), key=lambda kv: kv[1], reverse=True)
    letters = ''.join([letter for letter, frequency in sorted_by_value if frequency != 0])

    if len(letters) == 0:
        regular = get_filtered_freq_list(corpus, 10000, [], [], [])
        return ''.join(list(set(regular)-set(existent_letters_list)-set(nonexistent_letters)-set(global_exclude)))
    return letters


def get_token(hangman_web_service):
    """Call the hangman web service to start a new game
    :param hangman_web_service: string with a url
    :return: dict of response
    """
    res = requests.get(hangman_web_service)
    return json.loads(res.text)


def send_guess(hangman_web_service, token, guess):
    """Call the hangman web service with a game token and a guess letter
    :param hangman_web_service: string of URL
    :param token: string id of a game
    :param guess: string of a letter to be guessed
    :return: dict of response
    """
    res = requests.get("{}&token={}&guess={}".format(hangman_web_service, token, guess))
    return json.loads(res.text)


def sentence_state_parser(state):
    """Parse the state returned in a response of a hangman web service call to get details of each word in sentence
    :param state: string from hangman web service
    :return: list of dict with details about each word in the sentence
    """
    game_words = state.split(' ')
    game_word_details = []

    for word in game_words:
        exist = []
        word_len = len(word)
        for idx, char in enumerate(word):
            if char != '_' and char.isalpha():
                exist.append({"letter": char, "position": idx})

        game_word_details.append({"word": word, "length": word_len, "exist": exist, "nonexist": [],
                                  "remaining": word_len-len(exist)})
    return game_word_details


def play_game(game_start, corpus, hangman_web_service, flags):
    """Call all the functions and play hangman
    :param game_start: dict of details from starting a game
    :param corpus: list of words
    :param hangman_web_service: string of a URL
    :param flags: string for verbose/non-verbose
    :return: list of status of prisoner and state of sentence on completion
    """
    state_details = sentence_state_parser(game_start["state"])
    global_exclude = []

    while game_start['remaining_guesses'] > 0:

        # Guess the word with maximum length first
        max_word_length = 0
        guess_word = state_details[0]
        guess_idx = 0
        for idx, word in enumerate(state_details):
            if word["remaining"] > 0 and word["length"] >= max_word_length:
                guess_idx = idx
                max_word_length = word["length"]
                guess_word = word

        # Get sequence of letters to guess
        filtered_letter_frequency = get_filtered_freq_list(corpus, guess_word["length"], guess_word["nonexist"],
                                                           guess_word["exist"], global_exclude)
        make_guess = send_guess(hangman_web_service, game_start['token'], filtered_letter_frequency[0])
        global_exclude.append(filtered_letter_frequency[0])
        new_state_details = sentence_state_parser(make_guess["state"])

        # Print messages for verbose mode
        if '-v' == flags:
            print("Guessing for (X)     :", guess_word)
            print("Guessing this letter :", filtered_letter_frequency[0])
            print("Possible Guesses     :", filtered_letter_frequency)
            print("Server Response      :", make_guess)
            print("New Details of (X)   :", new_state_details)

        # If the word that was attempted to be guessed had not change, append the letter the a non-exist list
        if new_state_details[guess_idx]["remaining"] == state_details[guess_idx]["remaining"]:
            new_state_details[guess_idx]["nonexist"].append(filtered_letter_frequency[0])

        # Replace old state with new state
        state_details = new_state_details[:]

        if make_guess['remaining_guesses'] != game_start['remaining_guesses']:
            game_start['remaining_guesses'] -= 1

        if make_guess['status'] != 'ALIVE':
            break
        game_start['state'] = make_guess['state']

    if "-v" == flags:
        print("The prisoner is: ", make_guess['status'])

    return [make_guess['status'], game_start['state']]


def get_corpus():
    """Read a file to build corpus
    :return: list of words
    """
    # Attempted with the Brown Corpus from nltk, but provided similar results.
    # corpus = brown.words()
    # corpus = list(word.strip().upper() for word in corpus)

    # Corpus is a list of 100,000 most commonly used words by Wikipedia.
    with open('wiki-100k.txt', 'r', encoding='utf8') as wordbank:
        corpus = wordbank.readlines()
    return list(word.strip().upper() for word in corpus)


def main():
    hangman_web_service = "http://gallows.hulu.com/play?code=shankak@purdue.edu"
    corpus = get_corpus()
    try:
        flags = sys.argv[1]
    except IndexError:
        flags = ""

    while True:
        game_start = get_token(hangman_web_service)
        status, state = play_game(game_start, corpus, hangman_web_service, flags)
        if "-v" == flags:
            print("{} - {}\n\n".format(status, state))


if __name__ == "__main__":
    main()