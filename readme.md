# Debugger for Asciidots


### The Asciidot language
The beautiful [Asciidot language](https://github.com/aaronduino/asciidots) 
develloped by Aaron Janse is inspired by ascii-art and electronic circuits.

You may want to try it online [here](https://asciidots.herokuapp.com/)
or buy cloning the [repo](https://github.com/aaronduino/asciidots).

    git clone https://github.com/aaronduino/asciidots
    cd asciidots
    python __main__.py samples/fibonnacci.dots -d

And you should see the dots in red moving along the lines...
But you will quickly find that you have troubles to understand more complex programs or debug them.

This is where this graphical debugger comes.

### The Graphical Debugger

#### Features
With this, you will be able to:
- play with the time and go back to see where dots comes from
- enjoy enven more the beauty of ascii-art with nice colors

And in the future
- Click on dots to see their values and id
- edit the code directly in the app
- Make gifs of your code 

#### Installation and use

In the folder you want:
    
    git clone https://github.com/ddorn/AsciidotsDebugger
    cd AsciidotsDebugger
    python debugger.py samples/fibonnaci.dots

And enjoy it !

### Remarks

This repo is a clone of my own fork of asciidots, this means that there can be a delay (and there will be) 
between an update of the official version of asciidots and the one in this repo.

I'm very open to suggestions, issues and PRs ;)

---

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
