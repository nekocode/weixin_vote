$(function(){
  var navTab = $('.nav-tab'),
      tabContent = document.querySelector('.tab-content'),
      wrapper = $('.wrapper'),
      tab1Height = wrapper.find('.ranking1').height() + 20 + 'px',
      tab2Height = wrapper.find('.ranking2').height() + 20 + 'px',
      isAnimating = false,
      startPosition = {};

  // 初始设置.tab-content的高度
  tabContent.style.height = tab1Height;

  var showFirstTab = function() {
    navTab.removeClass('show-last');
    wrapper.removeClass('show-last');
    tabContent.style.height = tab1Height;
  };

  var showLastTab = function() {
    navTab.addClass('show-last');
    wrapper.addClass('show-last');
    tabContent.style.height = tab2Height;
  };

  var startAnimation = function(event){
    if (!isAnimating) {
      // 只在按下左键时触发
      if ('button' in event && event.button !== 0) {
        return;
      }
      isAnimating = true;
      startPosition = {
        pageX: event.pageX || event.touches.item(0).pageX,
        pageY: event.pageY || event.touches.item(0).pageY,
      };
    }
  };

  var animate = function(event){
    if (isAnimating) {
      var xDistance = (event.pageX || event.touches.item(0).pageX) - startPosition.pageX,
          yDistance = Math.abs((event.pageY || event.touches.item(0).pageY) - startPosition.pageY);

      // 竖直方向偏移较大时不切换
      if (3 * yDistance > Math.abs(xDistance)) {
        isAnimating = false;
      }
      else if (xDistance < -8) {
        showLastTab();
        isAnimating = false;
      }
      else if (xDistance > 8) {
        showFirstTab();
        isAnimating = false;
      }
    }
  };

  var endAnimation = function(){
    isAnimating = false;
  };

  var startEvents, animateEvents, endEvents;
  if ('ontouchstart' in document) {
    startEvents = 'touchstart';
    animateEvents = 'touchmove';
    endEvents = 'touchend touchcancel';
  }
  else if ('onpointerdown' in document) {
    startEvents = 'pointerdown';
    animateEvents = 'pointermove';
    endEvents = 'pointerup pointercancel';
  }
  else if ('onMSPointerDown' in document) {
    startEvents = 'MSPointerDown';
    animateEvents = 'MSPointerMove';
    endEvents = 'MSPointerUp MSPointerCancel';
  }
  else if ('onmousedown' in document) {
    startEvents = 'mousedown';
    animateEvents = 'mousemove';
    endEvents = 'mouseup mousecancel';
  }
  else {
    startEvents = 'touchstart pointerdown MSPointerDown mousedown';
    animateEvents = 'touchmove pointermove MSPointerMove mousemove';
    endEvents = 'touchend pointerup MSPointerUp mouseup touchcancel pointercancel MSPointerCancel mousecancel';
  }

  $('body')
    .on(startEvents, startAnimation)
    .on(animateEvents, animate)
    .on(endEvents, endAnimation);

  $('.nav-tab').on('click', 'li', function(){
    if (this.className.indexOf('active') !== -1){
      return;
    }
    if ($(this).next().length){
      showFirstTab();
    }
    else {
      showLastTab();
    }
  });
});
