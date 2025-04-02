// Custom datepicker styling
$(document).ready(function() {
  // Apply styles when a datepicker is shown
  $(document).on('show', '.datepicker', function() {
    setTimeout(function() {
      // Main container
      $('.datepicker-dropdown').css({
        'background-color': 'var(--PurpleDiscreet)',
        'border-color': 'var(--Accent_2)'
      });
      
      // All elements inside the datepicker
      $('.datepicker-dropdown *').css({
        'background-color': 'var(--PurpleDiscreet)',
        'color': 'var(--WhiteDiscreet)'
      });
      
      // Day cells
      $('.datepicker-dropdown .day').css({
        'background-color': 'var(--PurpleDiscreet)',
        'color': 'var(--WhiteDiscreet)'
      });
      
      // Selected day
      $('.datepicker-dropdown .active').css({
        'background-color': 'orange',
        'background-image': 'none',
        'color': 'var(--White)'
      });
      
      // Fix any border issues
      $('.anvil-datepicker .form-control').css({
        'border': '1px solid var(--Accent_2)',
        'padding': '4px 8px',
        'height': 'auto'
      });
    }, 10); // Small delay to ensure datepicker is rendered
  });
  
  // Add hover effects
  $(document).on('mouseenter', '.datepicker .day, .datepicker .prev, .datepicker .next, .datepicker .datepicker-switch', function() {
    $(this).css({
      'background-color': 'var(--Accent_2)',
      'color': 'var(--White)'
    });
  });
  
  $(document).on('mouseleave', '.datepicker .day:not(.active), .datepicker .prev, .datepicker .next, .datepicker .datepicker-switch', function() {
    $(this).css({
      'background-color': 'var(--PurpleDiscreet)',
      'color': 'var(--WhiteDiscreet)'
    });
  });
});
