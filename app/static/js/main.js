document.addEventListener("DOMContentLoaded", () => {
  const optionMatches = (option, query) =>
    !query || option.textContent.toLowerCase().includes(query);

  const optionMatchesController = (option, controllerValue) =>
    !option.dataset.controllerValue ||
    !controllerValue ||
    option.dataset.controllerValue === controllerValue;

  const refreshSelectOptions = (select) => {
    const searchInput = document.querySelector(
      `[data-select-filter="${select.id}"]`,
    );
    const controllerId = select.dataset.controllerSelect;
    const controller = controllerId ? document.getElementById(controllerId) : null;
    const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
    const controllerValue = controller ? controller.value : "";

    let visibleChoiceCount = 0;

    Array.from(select.options).forEach((option) => {
      if (!option.value) {
        option.hidden = false;
        return;
      }

      option.hidden = !(
        optionMatches(option, query) &&
        optionMatchesController(option, controllerValue)
      );

      if (!option.hidden) {
        visibleChoiceCount += 1;
      }
    });

    const placeholder = Array.from(select.options).find((option) => !option.value);
    if (placeholder && select.dataset.dependentSelect) {
      if (!controllerValue) {
        placeholder.textContent =
          select.dataset.emptyLabel || "Select an option first";
      } else if (visibleChoiceCount === 0) {
        placeholder.textContent =
          select.dataset.noResultsLabel || "No records found";
      } else {
        placeholder.textContent = "Select course";
      }
      placeholder.selected = !select.value;
    }

    const selectedOption = select.selectedOptions[0];
    if (selectedOption && selectedOption.hidden) {
      select.value = "";
    }
  };

  document.querySelectorAll("[data-select-filter]").forEach((searchInput) => {
    const selectId = searchInput.dataset.selectFilter;
    const select = document.getElementById(selectId);

    if (!select) {
      return;
    }

    searchInput.addEventListener("input", () => {
      refreshSelectOptions(select);
    });
  });

  document.querySelectorAll("[data-dependent-select]").forEach((select) => {
    const controller = document.getElementById(select.dataset.controllerSelect);

    if (!controller) {
      return;
    }

    controller.addEventListener("change", () => {
      select.value = "";
      refreshSelectOptions(select);
    });
    refreshSelectOptions(select);
  });
});
