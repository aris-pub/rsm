// touch.js
//
// A touch page: html.touch, which the builder's pre-paint script sets on a
// device with no hover and a coarse pointer, and which a page that shows RSM in
// a frame can set too (the docs' Touch switch). Code that must act as on a
// phone reads this class, not the device, so a mouse on a touch page gets what
// a finger gets. Read at each use, since the class can change.

export const isTouch = () => document.documentElement.classList.contains("touch");
