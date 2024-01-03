from django.http import JsonResponse
from django.utils.text import slugify
from django.views import View
from .models import Position, Candidate

class BallotGeneratorMixin:
    def generate_ballot(self, positions, display_controls=False):
        output = ""
        candidates_data = ""
        num = 1

        for position in positions:
            name = position.name
            position_name = slugify(name)
            candidates = Candidate.objects.filter(position=position)

            # Initialize instruction with a default value
            instruction = "Select only one candidate"

            for candidate in candidates:
                if position.max_vote > 1:
                    instruction = f"You may select up to {position.max_vote} candidates"
                    input_box = f'<input type="checkbox" value="{candidate.id}" class="flat-red {position_name}" name="{position_name}[]">'
                else:
                    instruction = "Select only one candidate"
                    input_box = f'<input value="{candidate.id}" type="radio" class="flat-red {position_name}" name="{position_name}">'

                image = f"/media/{candidate.photo}"
                candidates_data += f'<li>{input_box}<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="{candidate.fullname}" data-bio="{candidate.bio}"><i class="fa fa-search"></i> Platform</button><img src="{image}" height="100px" width="100px" class="clist"><span class="cname clist">{candidate.fullname}</span></li>'

            up = 'disabled' if position.priority == 1 else ''
            down = 'disabled' if position.priority == len(positions) else ''

            output += f"""<div class="row">
                            <div class="col-xs-12">
                                <div class="box box-solid" id="{position.id}">
                                    <div class="box-header with-border">
                                        <h3 class="box-title"><b>{name}</b></h3>"""

            if display_controls:
                output += f"""<div class="pull-right box-tools">
                                    <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i></button>
                                    <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
                                </div>"""

            output += f"""</div>
                            <div class="box-body">
                                <p>{instruction}
                                    <span class="pull-right">
                                        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
                                    </span>
                                </p>
                                <div id="candidate_list">
                                    <ul>
                                        {candidates_data}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""

            position.priority = num
            position.save()
            num += 1
            candidates_data = ''

        return output

class YourViewClassName(BallotGeneratorMixin, View):
    def get(self, request, *args, **kwargs):
        positions = Position.objects.order_by('priority').all()
        output = self.generate_ballot(positions, display_controls=True)
        return JsonResponse(output, safe=False)
