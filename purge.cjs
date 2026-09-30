const { PurgeCSS } = require("purgecss");
const CleanCSS = require("clean-css");
const fs = require("fs");
const path = require("path");

const srcDir = "static/frontend/assets/css";
const outDir = `${srcDir}/purged`;


  const files = [
  'offers.css',
  'blog-detail.css',
  'offer-detail.css',
  'ride-detail.css',
  'user-login.css',
  'rides.css',
  'contact.css',
];


(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  const results = await new PurgeCSS().purge({
    content: [
      "**/templates/**/*.html",
      "static/frontend/assets/js/**/*.js",
      "!**/node_modules/**",
      "!**/venv/**",
      "!**/staticfiles/**",
    ],
    css: files.map((f) => `${srcDir}/${f}`),
    safelist: {
      standard: [
        /^show$/,
        /^active$/,
        /^collapse/,
        /^fade$/,
        /^modal/,
        /^open$/,
      ],
      deep: [/^slick/, /^swiper/, /^aos/, /^mfp/, /^animate/, /^flatpickr/],
    },
  });

  console.log("Files processed:", results.length);

  for (const r of results) {
    const base = path.basename(r.file);
    const name = base.replace(/(\.min)?\.css$/, ".purged.min.css");
    const before = fs.statSync(r.file).size;
    const min = new CleanCSS({ level: 2 }).minify(r.css).styles;
    fs.writeFileSync(`${outDir}/${name}`, min);
    console.log(
      `${base}: ${(before / 1024).toFixed(1)}KB -> ${(min.length / 1024).toFixed(1)}KB`,
    );
  }
})();
