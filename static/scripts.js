"use strict";

window.onload = (event) => {
    document.getElementById("open-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.add('open');
    });
    document.getElementById("close-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.remove('open');
    });
};