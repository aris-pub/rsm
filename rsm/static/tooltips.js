// tooltips.js
//
// Setup tooltips on <a> tags.
//

export function createTooltips() {
  $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster({
    theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
    minWidth: 100,
    maxWidth: 500,
    trigger: 'custom',
    triggerOpen: {
      mouseenter: true,
      touchstart: true
    },
    triggerClose: {
      click: true,
      mouseleave: true,
      originClick: true,
      touchleave: true
    },
    functionInit: function (instance, helper) {
      let target = $(helper.origin).attr("href");
      if (!target) {
        console.warn("Target does not have an href attribute");
        return;
      }
      let content = "";

      // escape '.' since it gets confused with a class
      target = target.replaceAll(".", "\\.");
      // escape ':' since it gets confused with the protocol
      target = target.replaceAll(":", "\\:");
      if (target == "#") {
        content = '<span class="error">target node has no label</span>';
        setTooltipContent(instance, content);
        helper.origin.classList.add("error");
        return;
      };

      let tag = $(target).prop('tagName');

      if (!$(target)[0]) {
        // console.error(`unknown target ${target}, tooltip cannot be created`);
        return;
      }

      let classes = $(target)[0].classList;

      let clone = undefined;

      if (["P", "LI", "FIGURE"].includes(tag)) {
        content = $(target).html();
        content = `<div>${content}</div>`;
      } else if (tag == "SPAN" && classes.contains("math")) {
        content = $(target).html();
        content = `<div>${content}</div>`;
      } else if (tag == "SPAN") {
        content = $(target).parent().html();
        content = `<div>${content}</div>`;
      } else if (tag == "DT") {
        content = $(target).next().html();
      } else if (tag == "TABLE") {
        content = $(target)[0].outerHTML;
      } else if (tag == "SECTION") {
        clone = $(target).clone();
        clone.children().slice(2).remove();
        stripHandrail(clone);
        clone.css('font-size', '0.7rem');
        content = clone.html();
      } else if (tag == "A") {
        content = $(target).parent().html();
        content = `<div>${content}</div>`;
      } else if (tag == "DIV") {
        switch (true) {
          case classes.contains("step"):
            clone = $(target).find(".statement").clone();
            stripHandrail(clone);
            clone.css('font-size', '0.7rem');
            content = clone.html();
            break;
          case Array.from(classes).filter(cls => ["math", "algorithm"].includes(cls)).length > 0:
            content = $(target).html();
            break;
          case Array.from(classes).filter(cls => ["paragraph", "mathblock", "theorem", "proposition", "remark", "bibitem"].includes(cls)).length > 0:
            clone = $(target).clone();
            stripHandrail(clone);
            content = $(clone).html();
            break;
          case true:
            console.log(`tooltip target DIV with unknown class: ${classes}`)
        }
      } else {
        console.log(`tooltip target with unknown tag ${tag}`);
      }

      setTooltipContent(instance, content);
    }
  });
}


function stripHandrail(hr) {
  hr.find(".hr-collapse-zone").remove();
  hr.find(".hr-menu-zone").remove();
  hr.find(".hr-border-zone").remove();
  hr.find(".hr-spacer-zone").remove();
  hr.find(".hr-info-zone").remove();
}

function setTooltipContent(tt, content) {
  // add .manuscriptwrapper so that all CSS rules apply inside the tooltip
  content = `<div class="manuscriptwrapper">${content}</div>`;
  tt.content($(content));
}
