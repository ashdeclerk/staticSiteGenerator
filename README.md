# Static Site Generator
This static site generator was made as part of the Boot.dev curriculum.

Start with markdown files in the `/content` directory. Then run `main.sh`, which
will delete everything in `/public` and replace it with an HTML-ified version
of those markdown files and start Python's built-in HTTP server on `http://localhost:8888`.
(You can, of course, push the contents of `/public` to a site hosting service.)

DO NOT STORE ANYTHING IN `/public` THAT YOU DON'T WANT DELETED!

## How it works
The rough outline is:
1. Delete everything in `/public`.
2. Copy static assets from `/static` to `/public`.
3. Convert each block of text from markdown files in `/content` to a tree of
   HTMLNode objects.
4. Join all of the HTMLNode blocks under a single parent for each page.
5. Convert said HTMLNode to an HTML string and inject it in the template.
6. Write that string to a file in `/public`.
