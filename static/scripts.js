"use strict";

window.onload = (event) => {
    document.getElementById("open-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.add('open');
    });
    document.getElementById("close-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.remove('open');
    });

    if ('wakeLock' in navigator) {
        let wakeLock = null;
        document.getElementById("keep-awake-field").style.display = "block";

        async function requestWakeLock() {
          if (wakeLock !== null && !wakeLock.released) return;

          try {
            wakeLock = await navigator.wakeLock.request('screen');

            // Listen for the 'release' event
            wakeLock.addEventListener('release', () => {
                console.log('Wake Lock was released');
            });
            console.log('Wake Lock active');
          } catch (err) {
            console.error('Wake lock request failed:', err);
          }
        }

        // Automatically release the wake lock when the page is hidden
        document.addEventListener('visibilitychange', () => {
            if (wakeLock !== null && document.hidden) {
              wakeLock.release()
                .then(() => console.log('Wake lock on page visibility change.'));
            } else if (!document.hidden) {
              requestWakeLock();
            }
        });

        document.getElementById("keep-awake-field").addEventListener('change', async event => {
            if (event.target.checked) {
                await requestWakeLock();
            } else if (wakeLock !== null) {
                wakeLock.release();
            }
        });
    }
};



// class WakeLockManager {
//   #sentinel = null;
//
//   get isActive() {
//     return this.#sentinel !== null && !this.#sentinel.released;
//   }
//
//   async acquire() {
//     if (this.isActive) return;
//     try {
//       this.#sentinel = await navigator.wakeLock.request('screen');
//       this.#sentinel.addEventListener('release', () => {
//         this.#sentinel = null;
//       });
//     } catch (err) {
//       console.error('Failed to acquire wake lock:', err);
//     }
//   }
//
//   async release() {
//     if (this.#sentinel) {
//       await this.#sentinel.release();
//       this.#sentinel = null;
//     }
//   }
// }