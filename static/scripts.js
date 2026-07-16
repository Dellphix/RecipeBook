"use strict";


window.onload = (event) => {
    
    /** Navigation */
    $("#open-nav").on('click', () => {
        $('.navigation').addClass('open');
    });
    $("#close-nav").on('click', () => {
        $('.navigation').removeClass('open');
    });

    /** Keep Awake */
    let keepAwake = $("#keep-awake");
    if ('wakeLock' in navigator && keepAwake.length) {
        let wakeLock = null;
        keepAwake.show();

        async function requestWakeLock() {
          if (wakeLock !== null && !wakeLock.released) return;

          try {
            wakeLock = await navigator.wakeLock.request('screen');

            // Listen for the 'release' event
            wakeLock.on('release', () => {
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

        $("#keep-awake-field").on('change', async event => {
            if (event.target.checked) {
                await requestWakeLock();
            } else if (wakeLock !== null) {
                wakeLock.release();
            }
        });
    }

    /** Add ingredient */
    let addIngredient = $("#add-ingredient");
    if (addIngredient.length) {
        addIngredient.on('click', (event) => {
            event.preventDefault();
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
                    const ingredientCount = $('.ingredient').length;
                    let ingredientBase = 'ingredient_set-' + ingredientCount; // They're zero indexed, so we can just add the count on
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
                    ingredientRecipeHidden.value = $('#id_ingredient_set-0-recipe').val();

                    ingredient.classList.remove('new-ingredient');
                    ingredient.classList.add('ingredient');
                    $('#ingredients').append(ingredient);

                    // Update form management
                    $('#id_ingredient_set-TOTAL_FORMS').val(ingredientCount + 1);
                  })
                .catch(error => {console.log(error)});

        });
    }
};