import random
import string

# Word categories for the game
WORD_LISTS = {
    'animals': ['elephant', 'giraffe', 'penguin', 'dolphin', 'kangaroo', 'cheetah', 'rhinoceros'],
    'countries': ['brazil', 'australia', 'germany', 'argentina', 'thailand', 'portugal', 'switzerland'],
    'technology': ['computer', 'keyboard', 'software', 'database', 'algorithm', 'internet', 'programming'],
    'sports': ['basketball', 'football', 'volleyball', 'baseball', 'swimming', 'tennis', 'badminton']
}

# ASCII art for hangman stages
HANGMAN_STAGES = [
    """
       ------
       |    |
       |
       |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |    |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |   /
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |   / \\
       |
    --------
    """
]

class HangmanGame:
    def __init__(self):
        self.max_attempts = 6
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.word = ""
        self.category = ""
        self.hint_used = False
        
    def choose_word(self):
        """Select a random category and word"""
        self.category = random.choice(list(WORD_LISTS.keys()))
        self.word = random.choice(WORD_LISTS[self.category]).lower()
        
    def display_word(self):
        """Display the word with guessed letters revealed"""
        display = ""
        for letter in self.word:
            if letter in self.guessed_letters:
                display += letter + " "
            else:
                display += "_ "
        return display.strip()
    
    def get_hint(self):
        """Reveal a random unguessed letter as a hint"""
        if self.hint_used:
            return "You've already used your hint!"
        
        unguessed = [letter for letter in self.word if letter not in self.guessed_letters]
        if unguessed:
            hint_letter = random.choice(unguessed)
            self.guessed_letters.add(hint_letter)
            self.hint_used = True
            return f"Hint: The letter '{hint_letter}' is in the word!"
        return "No hints available."
    
    def make_guess(self, guess):
        """Process a player's guess"""
        # Validate input
        if len(guess) != 1:
            return "Please enter a single letter."
        
        if guess not in string.ascii_lowercase:
            return "Please enter a valid letter (a-z)."
        
        if guess in self.guessed_letters:
            return "You've already guessed that letter!"
        
        # Add to guessed letters
        self.guessed_letters.add(guess)
        
        # Check if guess is correct
        if guess in self.word:
            return f"Good guess! '{guess}' is in the word."
        else:
            self.wrong_guesses += 1
            return f"Sorry, '{guess}' is not in the word."
    
    def is_game_won(self):
        """Check if the player has won"""
        return all(letter in self.guessed_letters for letter in self.word)
    
    def is_game_lost(self):
        """Check if the player has lost"""
        return self.wrong_guesses >= self.max_attempts
    
    def display_status(self):
        """Display current game status"""
        print("\n" + "="*50)
        print(HANGMAN_STAGES[self.wrong_guesses])
        print(f"Category: {self.category.upper()}")
        print(f"\nWord: {self.display_word()}")
        print(f"\nGuessed letters: {', '.join(sorted(self.guessed_letters)) if self.guessed_letters else 'None'}")
        print(f"Remaining attempts: {self.max_attempts - self.wrong_guesses}")
        print("="*50)
    
    def play(self):
        """Main game loop"""
        print("\n*** WELCOME TO HANGMAN ***")
        print("Guess the word one letter at a time!")
        print("Type 'hint' for a hint (one time use)")
        print("Type 'quit' to exit the game\n")
        
        # Choose a random word
        self.choose_word()
        
        # Game loop
        while True:
            self.display_status()
            
            # Get player input
            user_input = input("\nEnter your guess: ").lower().strip()
            
            # Check for special commands
            if user_input == 'quit':
                print(f"\nThanks for playing! The word was: {self.word}")
                break
            elif user_input == 'hint':
                print(self.get_hint())
                continue
            
            # Process the guess
            result = self.make_guess(user_input)
            print(result)
            
            # Check win condition
            if self.is_game_won():
                self.display_status()
                print("\n*** CONGRATULATIONS! YOU WON! ***")
                print(f"The word was: {self.word}")
                break
            
            # Check lose condition
            if self.is_game_lost():
                print(HANGMAN_STAGES[self.wrong_guesses])
                print("\n*** GAME OVER! ***")
                print(f"The word was: {self.word}")
                break
        
        # Ask to play again
        play_again = input("\nWould you like to play again? (yes/no): ").lower().strip()
        if play_again in ['yes', 'y']:
            self.__init__()  # Reset the game
            self.play()
        else:
            print("Thanks for playing Hangman!")

# Run the game
if __name__ == "__main__":
    game = HangmanGame()
    game.play()
