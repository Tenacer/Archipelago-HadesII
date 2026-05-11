# Hades II Archipelago
This is the APWorld side of the project to make Hades II compatible with the Archipelago Multiworld Randomizer.

## Goals
This multiworld implementation is an iteration from the one that exists for the original Hades game. In 
that one, you need to defeat Hades a set amount of times and there are some modifiers applied to make
your life a bit harder while doing it. For this implementation, I wanted to keep the same option for short games,
but given that Hades II is a much richer games I wanted to make an option that truly feels like a more 
traditional an Archipelago implementation, where you actually need items from the multiworld rather than just
grinding your game. For this reason I implemented a "True Ending" mode alongside it. 

So, let's review the two options available:

- Boss Defeats: This works in a similar way to the original Hades, but given that we have two routes there are 
already more options. Essentially, you select the number of necessary Underworld and Surface wins you need in
order to complete your goal. But, you can either combine the wins (so you could complete the goal just doing
one route) or count them separately (and therefore set the number of wins in each route you'll need).

- True Ending: With this, the two incantations needed to finish the game are required progression items you need 
to get from the multiworld and the necessary resources to make the incantations (Zodiac Sand, Void Lenses and a 
certain weapon) are also scattered in the multiworld. Once you're able to brew the incantation, another 
multiworld location check fires to keep items/locations balanced. In order to make this work, I also decided to 
change the rewards that you get from the final boss in each route to be multiworld items.

## Important options

There are some options that you can toggle that will significantly impact how you play your Hades II world. Here
they are summarized:

- Surface lock (default on): With this, the two incantations that are necessary to access the surface have an 
additional requirement gated behind a multiworld item. So this will potentially impact both types of goal that
you choose. This works in the same way that the True Ending incantations work.

- Weapon sanity: Weapon unlocks are checks and you receive the unlocks from the multiworld.

- Hidden aspect sanity: Hidden aspects of each weapon are checks and you receive the unlocks form the 
multiworld.
