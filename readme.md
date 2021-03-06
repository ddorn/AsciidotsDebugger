![Pi prime generation](assets/pi-primes.PNG)

# Debugger for Asciidots


### The Asciidot language
The beautiful [Asciidot language](https://github.com/aaronduino/asciidots) 
develloped by Aaron Janse is inspired by ascii-art and electronic circuits.

You may want to try it online [here](http://ajanse.me/asciidots/)
or by cloning the [repo](https://github.com/aaronduino/asciidots).

    git clone https://github.com/aaronduino/asciidots
    cd asciidots
    python __main__.py samples/fibonnacci.dots -d

And you should see the dots in red moving along the lines...
But you will quickly find that you have troubles to understand more complex programs or debug them.

This is where this graphical debugger comes.

### The Graphical Debugger

![There is a lot of colors](assets/colors.png)

#### Features
With this, you will be able to:
- play with the time and go back to see where dots comes from
- See the value and id of a dot when you hover it
- Zoom on your code
- Drag your code around in the windows to explore other parts
- But don't get lost in the code because you can reset the view
- Enjoy even more the beauty of ascii-art with nice colors and font
- Don't get distracted with the clean fullscreen
- And *more debug* mode to debug Asciidots itself

The *more debug* mode lets you:
- Know the class of the chars
- See where wraps lead

###### And in the future
- See the values of all dots at the same place
- See all output at the same time
- Edit the code directly in the app
- Give inputs to your code
- Make gifs of your code 


![Play with the time](assets/play_with_time.gif)

#### Controls

- <kbd>Right</kbd> : Next step
- <kbd>Left</kbd> : Previous step
- <kbd>Ctrl + Right</kbd> : 5th next step
- <kbd>Ctrl + Left</kbd> : 5th previous step
- <kbd>Ctrl + A</kbd> : Toggle auto advance in the execution
- <kbd>-</kbd> Decrease font size
- <kbd>+</kbd> or <kbd>=</kbd> Increase font size
- <kbd>Ctrl + B</kbd> Return to the beginning of the execution
- <kbd>Ctrl + R</kbd> Reset the view (size and pos)
- <kbd>Escape</kbd> Quit
- <kbd>Ctrl + M</kbd> Toggle the *more debug* mode
- Click and drag to move the code

![Drag your code](assets/move_around.gif)

#### Installation and use


The grapical interface is based on pygame, so you need to have it installed. 
The command line interface uses click, you must have it too.
Of course, you need an asciidots interpreter.

    pip install pygame click asciidots
    git clone https://github.com/ddorn/AsciidotsDebugger
    cd AsciidotsDebugger

That's it, now you can try it ! You can find more examples of Asciidots programs in the official repo along with the documentation of the language.
    
    python debugger.py samples/primes.dots

Enjoy it !

<p align="center"> 
<img src="assets/love.png">
</p>
---

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
