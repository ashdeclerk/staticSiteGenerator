# Static Site Generator
This static site generator was made as part of the Boot.dev curriculum.

Start with markdown files in the `/content` directory. Then run `build.sh`, which
will delete everything in `/docs` and replace it with an HTML-ified version
of those markdown files. You can then push the contents of `/docs` to a site
hosting service.

Note that `main.sh` will build the site and run a local server, which is useful
for previewing stuff (by opening up localhost:8888 with the server running).

DO NOT STORE ANYTHING IN `/docs` THAT YOU DON'T WANT DELETED!

## How it works
The rough outline is:
1. Delete everything in `/docs`.
2. Copy static assets from `/static` to `/docs`.
3. Convert each block of text from markdown files in `/content` to a tree of
   HTMLNode objects.
4. Join all of the HTMLNode blocks under a single parent for each page.
5. Convert said HTMLNode to an HTML string and inject it in the template.
6. Write that string to a file in `/docs`.

## Known Icks
(Technically not bugs per se, but things that I dislike.)
- We aren't doing nested inline elements, e.g. _italic and **bold** simultaneously_.
- Ordered lists ignore the original numbering, so a list that was originally 2) 3) 5) for whatever reason becomes  1) 2) 3).
- Ordered lists only handle numbers, not e.g. Roman numerals.
- We can't do sublists.
