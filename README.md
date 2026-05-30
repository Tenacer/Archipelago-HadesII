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

- **Boss Defeats**: This works in a similar way to the original Hades, but given that we have two routes there are 
already more options. Essentially, you select the number of necessary Underworld and Surface wins you need in
order to complete your goal. But, you can either combine the wins (so you could complete the goal just doing
one route) or count them separately (and therefore set the number of wins in each route you'll need).

- **True Ending**: With this, the two incantations needed to finish the game have altered requirements. Which means
that the necessary resources to make the incantations (Zodiac Sand, Void Lenses and two mystery resources) are also 
scattered in the multiworld. In practice, this means that the rewards for the final bosses of each route are 
randomized, so you will need to acquire the necessary resources, cast the incanation and finish the game as you
normally would. You can set how many Void Lenses and Zodiac Sands will be necessary and how many will be in the 
multiworld (via setting how many final boss kills give rewards).

## Important options

There are some options that you can toggle that will significantly impact how you play your Hades II world. Here
they are summarized:

- Surface lock (default on): With this, the two incantations that are necessary to access the surface have an 
additional requirement gated behind a multiworld item. So this will potentially impact both types of goal that
you choose. This works in the same way that the True Ending incantations work.

- Weapon sanity (default on): Weapon unlocks are checks and you receive the unlocks from the multiworld.

- Hidden aspect sanity (defaut on): Hidden aspects of each weapon are checks and you receive the unlocks form the 
multiworld.

- Cauldron sanity: All incantations from the cauldron are location checks and their rewards are randomized, 
except for True Ending or post-True Ending incantations. This can be a time intensive setting, so be ready for a 
long game.

- Fatesanity: not for the faint of heart. All prophecies are checks and their items are randomized, except (currently) 
for Epilogue and post True Ending prophecies. Probably the most time intensive setting.

## Installation

Installation should be relatively simple. Hades II uses r2modman (recommended) to load mods, which makes things 
much easier compared to how mods worked in Hades 1. Installation instructions are covered in the 
[documentation](https://github.com/Tenacer/Archipelago-HadesII/blob/main/worlds/hades_ii/docs/setup_en.md).

## Known issues

Please report any by submitting an issue through this Github repository.

## Acknowledgements

This implementation wouldn't be possible without the work from Archipelago team and the Hades II modding community, 
and really most of the credit should go to them. I'd also like to thank Jay_Playz2019 for getting this project on 
the road, and to NaixGames for doing the Hades 1 implementation, which this mod took a lot of inspiration from.
