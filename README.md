# AI TG spam banner

## What is this?
Just a quick bot I made out of frustration due to spam bots joining a group chat I manage.

Especially, there is this group of bots, that join _a lot_ (we've banned hundreds), even multiple times a day, that all promote this sort of (probably illegal) online casino, and it's just tiring banning it manually.


## How does it work?
Basically, every time an user / bot joins the group, it's name and tag gets sent to an LLM (in our case, firebase vertex ai) that estimates how likely it may be a bot.

In a scale from 0.00 and 1.00, if the likeliness of it being a bot is over 0.65, an alert to the alert group (could be a staff group chat) will be sent, if set.

If, instead, the likeliness is over 0.85, the account is automatically banned.

Same thing happens for the first message of every new user.

## Where did you get the inspiration?
Mainly from seeing the 110th bot joining and getting banned.

## Isn't banning one or two bots a day faster than writing a whole bot just to do this?
Yes.

## Why are you doing it?
That would be the first project I integrate AI in.

## It doesn't seem that much customizable, why is that?
Making it customizable is not much of a priority right not, it's midnight and i want to finish this and go to bed, if you want to abstract hardcoded parameters / strings, feel free to make a PR!