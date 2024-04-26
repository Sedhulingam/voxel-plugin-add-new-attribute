import fiftyone.operators as foo
import fiftyone.operators.types as types
import fiftyone.core.labels as fol

def get_label(samples, label_dicts):
    
    view = samples.select_labels(ids=[label_dicts[0]['label_id']])
    sample = view.first()
    label = sample[label_dicts[0]["field"]]
    if isinstance(label, fol._HasLabelList):
        label = getattr(label, label._LABEL_LIST_FIELD)[0]

    return sample, label

class NewAttribute(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="new_attribute",
            label="New Attribute",
            dynamic=True,
        )

    def resolve_placement(self, ctx):
        return types.Placement(
            types.Places.SAMPLES_VIEWER_ACTIONS,
            types.Button(
                label="Add New Attribute",
                prompt=True,
            ),
        )

    def resolve_input(self, ctx):
        inputs = types.Object()

        if len(ctx.selected_labels)==0:
            warning = types.Warning(label="No labels are selected")
            prop = inputs.view("warning", warning)
            prop.invalid = True 
            return types.Property(inputs, view=types.View(label="Edit label attributes"))

        if len(ctx.selected_labels) > 1:
            warning = types.Warning(label="Labels can only be edited one at a time but %d are selected" % len(ctx.selected_labels))
            prop = inputs.view("warning", warning)
            prop.invalid = True
            return types.Property(inputs, view=types.View(label="Edit label attributes"))

        inputs.str("class_name", label="Class Name")
        inputs.str("class_value", label="Class Value")

        return types.Property(inputs, view=types.View(label="Add New Attribute"))
  

    def execute(self, ctx):
        class_name = ctx.params["class_name"]
        class_value = ctx.params["class_value"]

        label_dict = ctx.selected_labels

        sample, label = get_label(ctx.dataset, label_dict)

        label[class_name] = class_value
      
        sample.save()


        ctx.dataset.save()
        ctx.trigger("reload_samples")
        ctx.trigger("reload_dataset")
    

def register(p):
    p.register(NewAttribute)
