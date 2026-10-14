---
name: model-driven-app-customization
description: "Customises Dynamics 365 model-driven apps: forms, views, business rules, business process flows, the command bar with Power Fx or JavaScript, JavaScript web resources using formContext and Xrm.WebApi, and PCF controls. Use when the user asks to change a form, show, hide, require, or default a field, add a button, build a business process flow, or write, review, or fix form JavaScript."
---

# Model-Driven App Customisation

## Pick the lightest tool that works

1. **Configuration** — form designer, views, column requirement level, business required, default values.
2. **Business rule** (scope *Entity* if it must also apply server-side) — show/hide, enable/disable, set required, set value, simple validation.
3. **Power Fx** — formula columns, modern command bar visibility and actions.
4. **JavaScript web resource** — anything needing logic, async calls, or events business rules can't handle.
5. **PCF control** — custom UI component.

## JavaScript web resources

Namespace per client/project, always pass the execution context, never use the deprecated `Xrm.Page`.

```javascript
var Impax = Impax || {};
Impax.Account = Impax.Account || {};

Impax.Account.onLoad = function (executionContext) {
    "use strict";
    const formContext = executionContext.getFormContext();
    formContext.getAttribute("<prefix>_customertype").addOnChange(Impax.Account.onCustomerTypeChange);
    Impax.Account.onCustomerTypeChange(executionContext);
};

Impax.Account.onCustomerTypeChange = function (executionContext) {
    const formContext = executionContext.getFormContext();
    const type = formContext.getAttribute("<prefix>_customertype").getValue();
    const isCorporate = type === 100000001;            // name the option values in a constants object in real code
    formContext.getControl("<prefix>_kraPin").setVisible(isCorporate);
    formContext.getAttribute("<prefix>_kraPin").setRequiredLevel(isCorporate ? "required" : "none");
};

Impax.Account.loadPrimaryContact = async function (formContext) {
    const accountId = formContext.data.entity.getId().replace(/[{}]/g, "");
    try {
        const result = await Xrm.WebApi.retrieveRecord("account", accountId, "?$select=name&$expand=primarycontactid($select=fullname,mobilephone)");
        return result.primarycontactid;
    } catch (e) {
        Xrm.Navigation.openErrorDialog({ message: "Could not load the primary contact." });
    }
};
```

Register handlers with **"Pass execution context as first parameter"** ticked and the function name fully qualified (`Impax.Account.onLoad`).

### Rules

- Async only (`Xrm.WebApi`, `async/await`) — no synchronous XHR.
- Use `OnSave` with `executionContext.getEventArgs().preventDefault()` for blocking validation; prefer server-side (plugin/business rule) for validation that must hold for imports/integrations too.
- Check `formContext.ui.getFormType()` (1 = Create, 2 = Update) where behaviour differs.
- Don't touch the DOM (`document.getElementById`) — unsupported and breaks on updates.
- Keep option-set values, schema names, and messages in one constants object per file.
- Web resource naming: `<prefix>_/scripts/account.form.js`.
- Debug with browser DevTools (Sources → search the web resource) and Monitor.

## Forms & views

- Fewer tabs/subgrids/quick views on load = faster form. Collapse rarely-used tabs; consider loading subgrids on tab expand.
- One main form per role group where possible; use **form order + security roles** to target forms.
- Views: only needed columns; avoid `contains` filters on large tables; set the right default view.

## Business process flows

Stages map to the real process the client described; required steps only where the process truly gates. Remember BPFs are their own table (security roles need privileges on it).

## Modern commanding

Command designer in the app designer. Visibility with Power Fx (e.g. `!IsBlank(Self.Selected.Item.'Primary Contact')`); action either Power Fx or a JavaScript function (pass `PrimaryControl` for the form context).

## Review checklist

- [ ] No `Xrm.Page`, no DOM manipulation, no sync calls.
- [ ] Execution context passed; functions namespaced.
- [ ] Logic that must apply to all channels is not only in JS.
- [ ] Tested as a non-admin role, on create and update, and on the mobile app if in scope.
