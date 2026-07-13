"use strict";

window.onload = (event) => {

    /** Navigation */
    document.getElementById("open-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.add('open');
    });
    document.getElementById("close-nav").addEventListener('click', () => {
        document.querySelector('.navigation').classList.remove('open');
    });

    /** Keep Awake */
    if ('wakeLock' in navigator && document.getElementById("keep-awake")) {
        let wakeLock = null;
        document.getElementById("keep-awake").style.display = "block";

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

    /** Add ingredient */
    if (document.getElementById("add-ingredient")) {
        document.getElementById("add-ingredient").addEventListener('click', () => {
            let url = window.location.origin + "/ajax-ingredient";
            fetch(url, {method: 'GET'})
                .then(response => {
                    // When the page is loaded convert it to text
                    return response.text()
                  })
                .then(html => {
                    const parser = new DOMParser()
                    const parsedHtml = parser.parseFromString(html, "text/html")

                    // Update field ids etc
                    const ingredient = parsedHtml.querySelector('.new-ingredient');
                    const ingredientCount = document.querySelectorAll('.ingredient').length;
                    let ingredientBase = 'ingredient_set-' + ingredientCount; // They're zero indexed, so we can just add the count on
                    console.log(parsedHtml, ingredient);
                    let ingredientQuantityInput = ingredient.querySelector('#id_ingredient_set-0-quantity');
                    ingredientQuantityInput.id = 'id_' + ingredientBase + '-quantity';
                    ingredientQuantityInput.name = ingredientBase + '-quantity';
                    let ingredientUnitInput = ingredient.querySelector('#id_ingredient_set-0-unit');
                    ingredientUnitInput.id = 'id_' + ingredientBase + '-unit';
                    ingredientUnitInput.name = ingredientBase + '-unit';
                    let ingredientDescriptionInput = ingredient.querySelector('#id_ingredient_set-0-description');
                    ingredientDescriptionInput.id = 'id_' + ingredientBase + '-description';
                    ingredientDescriptionInput.name = ingredientBase + '-description';
                    let ingredientDeleteInput = ingredient.querySelector('#id_ingredient_set-0-DELETE');
                    ingredientDeleteInput.id = 'id_' + ingredientBase + '-DELETE';
                    ingredientDeleteInput.name = ingredientBase + '-DELETE';
                    
                    // hidden fields
                    let ingredientIdHidden = ingredient.querySelector('#id_ingredient_set-0-id');
                    ingredientIdHidden.id = 'id_' + ingredientBase + '-id';
                    ingredientIdHidden.name = ingredientBase + '-id';
                    let ingredientRecipeHidden = ingredient.querySelector('#id_ingredient_set-0-recipe');
                    ingredientRecipeHidden.id = 'id_' + ingredientBase + '-recipe';
                    ingredientRecipeHidden.name = ingredientBase + '-recipe';
                    ingredientRecipeHidden.value = document.getElementById('id_ingredient_set-0-recipe').value;

                    ingredient.classList.remove('new-ingredient');
                    ingredient.classList.add('ingredient');
                    document.getElementById('ingredients').appendChild(ingredient)

                    // Update form management
                    document.getElementById('id_ingredient_set-TOTAL_FORMS').value = ingredientCount + 1;
                  })
                .catch(error => {console.log(error)});

        });
    }
};