cutup
=====

"Cut up" a poem or essay, then drag and rearrange the pieces.

This app automates the common English/Language Arts teaching technique of cutting up a poem, essay, etc. into lines or paragraphs--then having the students sort them into a coherent order.

**Technical**

Cutup uses jQuery-UI for the draggable elements.

The Python web framework Flask takes the text input, parses it into individual lines or paragraphs, (cleans it up..though this needs improvement), and produces a randomized list.

**TODO**

- [x] Friendly instructions on the submit page.
- [x] Header and footer Jinja templates
- [ ] A "reshuffle" button
- [ ] Optional labels for 5-paragraph essays (Intro, Body1, ..., Conclusion)
- [x] Persistent urls for submitted texts
- [x] Flash animation 
- [ ] Touchscreen support
- [ ] Make pretty--less washed out colors? Center text?
