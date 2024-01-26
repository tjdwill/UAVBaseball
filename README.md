# CoDrone EDU Baseball
This project aims to emulate running bases reminiscent to the game of baseball using Robolink's CoDrone EDU.

- [Learning the Drone](https://youtu.be/gT2dIVrDKJQ)
- [Identifying Bases](https://youtu.be/n5RHxK8Ozew)
- [Rounding Multiple Bases](https://youtu.be/xHTBC7PvPYI)

## Retrospective (26 January 2024)

This project was unusual in the sense that every subsystem worked individually but not together. As explained in the third video, the drone was able to take off, land, sense the correct base, and then fly the next one in the correct direction. However, when multiple bases are traversed, there an error typically arose after first base. I've looked over the program logic multiple times and am unable to see the source of the error w.r.t software, so I am inclined to conclude that the problem is based in the hardware. It is possible that crashes during testing could have affected the drone such that the program would not work properly with this specific CoDrone EDU but may work with another one. The drone itself, however, is still operable, so if it is indeed a hardware issue, it is likely a subtle one. If it is _not_ a hardware issue, then that means there is a gap in my understanding of how the drone works (which is _certainly_ plausible).

I will not consider this project a success in terms of delivering the desired result. However, the process of working on this project led to palpable growth as a programmer and a system designer. I was able to successfully implement a context manager, extending the capabilities of the manufacturer's code. To me, this reinforced the value of tooling when it comes to thinking about a problem. Abstracting away the details of pairing and disconnecting the drone allowed more time and mental energy to be spent on the more abstract aspects of the project's code. It also safeguarded against errors.

As mentioned previously, this was also a project in which I improved my programming. I used text file logging for the first time and was able to more clearly identify when certain features or modules from the Python Standard Library would prove useful (or unnecessary). The modular structure of the program was an attempt to incorporate some of the ideas I'd been reading about functional programming, namely composing or leveraging simple functions to give rise to complex behaviors. Finally, this project was a great exercise in performing an investigation into a codebase to resolve a discrepancy between my understanding/intuition for a given behavior and the actual result. 

### What does it mean to represent an idea?

One lesson learned that is difficult to articulate is the importance of interpretation to the expression of an idea. There was no way the drone would actually be able to play baseball, but identifying key characteristics of the game allowed the implementation of behaviors that emulate it. Again, it's difficult to articulate, but the idea is that the spirit or essence of a thing is more important in the role of identification than its implementation details. Is it the four legs that make a chair or the fact that it's a single unit whose purpose is to provide a place for an individual to sit? The existence of three-legged chairs means the answer can't the former (but this doesn't necessarily mean the latter is the correct answer either).

When attempting to program a complex idea `X`, I tend to become a little overwhelmed due to trying to port the idea one-to-one into code; I make the task more difficult than necessary. Instead, I think my focus should be on identifying key aspects of `X` that will allow a human observer to identify the implementation `Y` as an **instance** of `X`. I'm reminded of a philosophy class I took in college where we discussed Plato's theory of Forms; maybe the above idea is related.
