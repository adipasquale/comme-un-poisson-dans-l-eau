module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("11ty_input/*.css");
  eleventyConfig.addPassthroughCopy("images");
  eleventyConfig.addPassthroughCopy("favicon");

  eleventyConfig.addWatchTarget("commeunpoissondansleau.db");

  eleventyConfig.addFilter("displayDate", function (date) {
    return new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' });
  });

  return {
    dir: {
      input: "11ty_input",
      output: "11ty_output",
      layouts: "_layouts"
    },
    markdownTemplateEngine: "njk"
  }
}
