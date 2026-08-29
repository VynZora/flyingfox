/*============================================================
Template Name   : Touria
Description     : Travel Agency And Tour HTML5 Template
Author          : LunarTemp
Version         : 1.0
==============================================================*/

(function ($) {
  "use strict";

  // multi level dropdown menu
  $(".dropdown-menu a.dropdown-toggle").on("click", function (e) {
    if (!$(this).next().hasClass("show")) {
      $(this).parents(".dropdown-menu").first().find(".show").removeClass("show");
    }
    var $subMenu = $(this).next(".dropdown-menu");
    $subMenu.toggleClass("show");

    $(this)
      .parents("li.nav-item.dropdown.show")
      .on("hidden.bs.dropdown", function (e) {
        $(".dropdown-submenu .show").removeClass("show");
      });
    return false;
  });

  //Header Search
  if ($(".search-box-outer").length) {
    $(".search-box-outer").on("click", function () {
      $("body").addClass("search-active");
    });
    $(".close-search").on("click", function () {
      $("body").removeClass("search-active");
    });
  }

  // data-background
  $(document).on("ready", function () {
    $("[data-background]").each(function () {
      $(this).css("background-image", "url(" + $(this).attr("data-background") + ")");
    });
  });

  // sidebar popup
  $(".sidebar-btn").on("click", function () {
    $(".sidebar-popup").addClass("open");
    $(".sidebar-wrapper").addClass("open");
  });
  $(".close-sidebar-popup, .sidebar-popup").on("click", function () {
    $(".sidebar-popup").removeClass("open");
    $(".sidebar-wrapper").removeClass("open");
  });

  // wow init
  new WOW().init();

  // hero slider
  $(".hero-slider").owlCarousel({
    items: 1,
    loop: true,
    nav: true,
    dots: true,
    margin: 0,
    autoplay: true,
    autoplayHoverPause: true,
    autoplayTimeout: 5000,
    navText: ["<i class='far fa-long-arrow-left'></i>", "<i class='far fa-long-arrow-right'></i>"],
    onInitialized: animateSlide,
    onChanged: animateSlide,
  });

  // animate slide
  function animateSlide(event) {
    let elements = $(".owl-item").eq(event.item.index).find("[data-animation]");
    elements.each(function () {
      let el = $(this),
        delay = el.data("delay"),
        duration = el.data("duration"),
        anim = "animated " + el.data("animation");

      el.css({
        "animation-delay": delay,
        "animation-duration": duration,
      });

      el.addClass(anim).one("animationend", () => el.removeClass(anim));
    });
  }

  // banner-slider
  $(".banner-slider").owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    dots: true,
    navText: ["<i class='far fa-angle-left'></i>", "<i class='far fa-angle-right'></i>"],
    autoplay: false,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 2,
      },
      1200: {
        items: 3,
      },
    },
  });

  // tour-slider
  $(".tour-slider").owlCarousel({
    loop: true,
    margin: 25,
    nav: true,
    dots: false,
    navText: ["<i class='far fa-angle-left'></i>", "<i class='far fa-angle-right'></i>"],
    autoplay: false,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 2,
      },
      1200: {
        items: 2,
      },
    },
  });

  // tour-single-slider
  $(".tour-single-slider").owlCarousel({
    loop: true,
    margin: 0,
    nav: true,
    dots: false,
    navText: ["<i class='far fa-long-arrow-left'></i>", "<i class='far fa-long-arrow-right'></i>"],
    autoplay: false,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 1,
      },
      1000: {
        items: 1,
      },
    },
  });

  // activity-slider
  $(".activity-slider").owlCarousel({
    loop: true,
    margin: 25,
    nav: true,
    dots: false,
    navText: ["<i class='far fa-angle-left'></i>", "<i class='far fa-angle-right'></i>"],
    autoplay: false,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 3,
      },
      1200: {
        items: 4,
      },
    },
  });

  // category-slider
  $(".category-slider").owlCarousel({
    loop: true,
    margin: 50,
    nav: true,
    dots: false,
    navText: ["<i class='far fa-angle-left'></i>", "<i class='far fa-angle-right'></i>"],
    autoplay: false,
    responsive: {
      0: {
        items: 2,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 4,
      },
      1200: {
        items: 5,
      },
    },
  });

  // partner-slider
  var isCenter = $(".partner-slider").data("center") == true;
  $(".partner-slider").owlCarousel({
    loop: true,
    margin: 25,
    nav: false,
    navText: ["<i class='icofont-long-arrow-left'></i>", "<i class='icofont-long-arrow-right'></i>"],
    dots: false,
    autoplay: true,
    center: isCenter,
    responsive: {
      0: {
        items: 2,
      },
      600: {
        items: 3,
      },
      1000: {
        items: 6,
      },
    },
  });

  // testimonial-slider
  $(".testimonial-slider").owlCarousel({
    loop: true,
    margin: 20,
    nav: false,
    dots: true,
    autoplay: true,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 2,
      },
      1200: {
        items: 2,
      },
    },
  });

  // preloader
 $(window).on("load", function () {
   $(".preloader").delay(3000).fadeOut(500);
 });

  // fun fact counter
  $(".counter").countTo();
  $(".counter-box").appear(
    function () {
      $(".counter").countTo();
    },
    {
      accY: -100,
    },
  );

  // magnific popup init
  $(".popup-gallery").magnificPopup({
    delegate: ".popup-img",
    type: "image",
    gallery: {
      enabled: true,
    },
  });

  $(".popup-youtube, .popup-vimeo, .popup-gmaps").magnificPopup({
    type: "iframe",
    mainClass: "mfp-fade",
    removalDelay: 160,
    preloader: false,
    fixedContentPos: false,
  });

  // progress bar
  $(document).ready(function () {
    var progressBar = $(".progress");
    if (progressBar.length) {
      progressBar.each(function () {
        var Self = $(this);
        Self.appear(function () {
          var progressValue = Self.data("value");
          Self.find(".progress-bar").animate(
            {
              width: progressValue + "%",
            },
            1000,
          );
        });
      });
    }
  });

  // case filter
  $(window).on("load", function () {
    if ($(".filter-box").children().length > 0) {
      $(".filter-box").isotope({
        itemSelector: ".filter-item",
        masonry: {
          columnWidth: 1,
        },
      });

      $(".filter-btn").on("click", "li", function () {
        var filterValue = $(this).attr("data-filter");
        $(".filter-box").isotope({ filter: filterValue });
      });

      $(".filter-btn li").each(function () {
        $(this).on("click", function () {
          $(this).siblings("li.active").removeClass("active");
          $(this).addClass("active");
        });
      });
    }
  });

  // scroll to top
  $(window).scroll(function () {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
      $("#scroll-top").addClass("active");
    } else {
      $("#scroll-top").removeClass("active");
    }
  });

  $("#scroll-top").on("click", function () {
    $("html, body").animate({ scrollTop: 0 }, 1500);
    return false;
  });

  // navbar fixed top
  $(window).scroll(function () {
    if ($(this).scrollTop() > 50) {
      $(".navbar").addClass("fixed-top");
    } else {
      $(".navbar").removeClass("fixed-top");
    }
  });

  // countdown
  $("[data-countdown]").each(function () {
    let finalDate = $(this).data("countdown");
    $(this).countdown(finalDate, function (event) {
      $(this).html(
        event.strftime(
          '<div class="time-wrap">' +
            '<span class="time"><span>%-D</span><span class="unit">Day%!D</span></span>' +
            ' <span class="divider">:</span> ' +
            '<span class="time"><span>%H</span><span class="unit">Hour%!H</span></span>' +
            ' <span class="divider">:</span> ' +
            '<span class="time"><span>%M</span><span class="unit">Min%!M</span></span>' +
            ' <span class="divider">:</span> ' +
            '<span class="time"><span>%S</span><span class="unit">Sec%!S</span></span>' +
            "</div>",
        ),
      );
    });
  });

  // slimselect
  document.querySelectorAll(".select")?.forEach((select) => {
    const slimSearch = select.dataset.slimSearch === "true";
    new SlimSelect({
      select: select,
      settings: {
        showSearch: slimSearch,
        searchPlaceholder: "Search...",
      },
    });
  });

  // flatpickr date & time
  document.querySelectorAll(".date-picker")?.forEach((el) => {
    const dateTime = el.dataset.datetime === "true";
    flatpickr(el, {
      enableTime: dateTime,
      time_24hr: false,
      dateFormat: dateTime ? "d M Y, h:i K" : "d M Y",
      prevArrow: "<i class='far fa-chevron-left'></i>",
      nextArrow: "<i class='far fa-chevron-right'></i>",
      disableMobile: true,
    });
  });

  // copywrite date
  let date = new Date().getFullYear();
  $("#date").html(date);

  // price range slider
  if ($(".price-range").length) {
    $(".price-range").slider({
      range: true,
      min: 0,
      max: 999,
      values: [100, 500],
      slide: function (event, ui) {
        $("#price-amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
      },
    });
    $("#price-amount").val("$" + $(".price-range").slider("values", 0) + " - $" + $(".price-range").slider("values", 1));
  }

  // flexslider
  if ($(".flexslider-thumbnails").length) {
    $(".flexslider-thumbnails").flexslider({
      animation: "slide",
      controlNav: "thumbnails",
    });
  }

  //cart quantity
  ($(".plus-btn").on("click", function () {
    var i = $(this).closest(".cart-qty").children(".quantity").get(0).value++,
      c = $(this).closest(".cart-qty").children(".minus-btn");
    i > 0 && c.removeAttr("disabled");
  }),
    $(".minus-btn").on("click", function () {
      2 == $(this).closest(".cart-qty").children(".quantity").get(0).value-- && $(this).attr("disabled", "disabled");
    }));

  // auth password view
  $(".password-view").on("click", function () {
    var pwd = document.getElementById("password");
    if (pwd.type === "password") {
      pwd.type = "text";
      $(this).addClass("show");
    } else {
      pwd.type = "password";
      $(this).removeClass("show");
    }
  });

  // profile image btn
  $(".profile-img-btn").on("click", function () {
    $(".profile-img-file").click();
  });

  // banner-img
  $(".banner-img-wrap .img-item").on("mouseenter", function () {
    $(this).addClass("active").siblings().removeClass("active");
  });

  // price slider
  if ($(".price-range").length) {
    $(".price-range").slider({
      step: 500,
      range: true,
      min: 0,
      max: 10000,
      values: [1500, 5000],
      slide: function (event, ui) {
        $(".priceRange").val("$" + ui.values[0].toLocaleString() + " - $" + ui.values[1].toLocaleString());
      },
    });
    $(".priceRange").val(
      "$" + $(".price-range").slider("values", 0).toLocaleString() + " - $" + $(".price-range").slider("values", 1).toLocaleString(),
    );
  }

  // bootstrap tooltip enable
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
})(jQuery);
