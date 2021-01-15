(function($){
  $(function(){

    $('.sidenav').sidenav();
    $('.dropdown-trigger').dropdown();
	  $('.materialboxed').materialbox();
    $('.collapsible').collapsible();
    $('.carousel.carousel-slider').carousel({
        fullWidth: true,
        indicators: true
    });
    $('select').formSelect();
    /*$('.datepicker').datepicker({'format': 'yyyy-mm-dd'});*/
    $('.datepicker').datepicker({
      format: 'yyyy-mm-dd',
      i18n: {
        cancel:   gettext('Cancel'),
        clear:   gettext('Clear'),
        done:   gettext('Ok'),
        months: [
          gettext('January'),
          gettext('February'),
          gettext('March'),
          gettext('April'),
          gettext('May'),
          gettext('June'),
          gettext('July'),
          gettext('August'),
          gettext('September'),
          gettext('October'),
          gettext('November'),
          gettext('December')
        ],
        monthsShort: [
          gettext('Jan'),
          gettext('Feb'),
          gettext('Mar'),
          gettext('Apr'),
          gettext('May'),
          gettext('Jun'),
          gettext('Jul'),
          gettext('Aug'),
          gettext('Sep'),
          gettext('Oct'),
          gettext('Nov'),
          gettext('Dec')
        ],
        weekdays: [
          gettext('Sunday'),
          gettext('Monday'),
          gettext('Tuesday'),
          gettext('Wednesday'),
          gettext('Thursday'),
          gettext('Friday'),
          gettext('Saturday')
        ],
        weekdaysShort: [
          gettext('Sun'),
          gettext('Mon'),
          gettext('Tue'),
          gettext('Wed'),
          gettext('Thu'),
          gettext('Fri'),
          gettext('Sat')
        ],
        weekdaysAbbrev: [
          pgettext('Sunday abbrev', 'S'),
          pgettext('Monday abbrev', 'M'),
          pgettext('Tuesday abbrev', 'T'),
          pgettext('Wednesday abbrev', 'W'),
          pgettext('Thursday abbrev', 'T'),
          pgettext('Friday abbrev', 'F'),
          pgettext('Saturday abbrev', 'S')
        ]
      }
    });
    
/*
    $toc = $('.toc-menu');

    if ($toc.length > 0) {

      construct_toc($toc);
      activate_scrollspy();
      $('.materialboxed').materialbox();

      setTimeout(function() { 
        if (initial_toc_activation) {
          // Make sure images have loaded
          $('body').imagesLoaded( function() {
            // images have loaded
            toc_pushpin($toc);
          });
        }
      }, 600);

    }*/

/*    $('.main-logo.pushpin').each(function() {
        var $this = $(this);
        var $target = $('#' + $(this).attr('data-target'));
        var $footer = $('footer');
        $this.pushpin({
          top: $target.offset().top,
          bottom: $footer.offset().top  - $this.height(),
          offset: -195
        });
    });
*/
  }); // end of document ready
})(jQuery); // end of jQuery name space
