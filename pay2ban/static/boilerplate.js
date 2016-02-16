document.addEventListener('DOMContentLoaded', function () {

  // Get all "navbar-burger" elements
  var $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {

    // Add a click event on each of them
    $navbarBurgers.forEach(function ($el) {
      $el.addEventListener('click', function () {

        // Get the target from the "data-target" attribute
        var target = $el.dataset.target;
        var $target = document.getElementById(target);

        // Toggle the class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

      });
    });
  }

});

function addEventListenerList(list, event, fn) {
    for (var i = 0, len = list.length; i < len; i++) {
        list[i].addEventListener(event, fn, false);
    }
}

// Find output DOM associated to the DOM element passed as parameter
function findOutputForSlider( element ) {
   var idVal = element.id;
   outputs = document.getElementsByTagName( 'output' );
   for( var i = 0; i < outputs.length; i++ ) {
     if ( outputs[ i ].htmlFor == idVal )
       return outputs[ i ];
   }
}

function getSliderOutputPosition( slider ) {
  // Update output position
  var newPlace,
      minValue;

  var style = window.getComputedStyle( slider, null );
  // Measure width of range input
  sliderWidth = parseInt( style.getPropertyValue( 'width' ), 10 );

  // Figure out placement percentage between left and right of input
  if ( !slider.getAttribute( 'min' ) ) {
    minValue = 0;
  } else {
    minValue = slider.getAttribute( 'min' );
  }
  var newPoint = ( slider.value - minValue ) / ( slider.getAttribute( 'max' ) - minValue );

  // Prevent bubble from going beyond left or right (unsupported browsers)
  if ( newPoint < 0 ) {
    newPlace = 0;
  } else if ( newPoint > 1 ) {
    newPlace = sliderWidth;
  } else {
    newPlace = sliderWidth * newPoint;
  }

  return {
    'position': newPlace + 'px'
  }
}

document.addEventListener( 'DOMContentLoaded', function () {
  // Get all document sliders
  var sliders = document.querySelectorAll( 'input[type="range"].slider' );
  [].forEach.call( sliders, function ( slider ) {
    var output = findOutputForSlider( slider );
    if ( output ) {
      if ( slider.classList.contains( 'has-output-tooltip' ) ) {
        // Get new output position
        var newPosition = getSliderOutputPosition( slider );

        // Set output position
        output.style[ 'left' ] = newPosition.position;
      }

      // Add event listener to update output when slider value change
      slider.addEventListener( 'input', function( event ) {
        if ( event.target.classList.contains( 'has-output-tooltip' ) ) {
          // Get new output position
          var newPosition = getSliderOutputPosition( event.target );

          // Set output position
          output.style[ 'left' ] = newPosition.position;
        }

        // Update output with slider value
        output.value = event.target.value;
      } );
    }
  } );
} );