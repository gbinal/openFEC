import sqlalchemy as sa
from flask.ext.restful import Resource

from webservices import args
from webservices import utils
from webservices import schemas
from webservices.common.models import (
    CandidateHistory, CommitteeHistory, CandidateCommitteeLink,
    ScheduleABySize, ScheduleAByState,
)


def candidate_aggregate(aggregate_model, label_columns, group_columns, kwargs):
    return CandidateHistory.query.with_entities(
        CandidateHistory.candidate_id,
        aggregate_model.cycle,
        sa.func.sum(aggregate_model.total).label('total'),
        *label_columns
    ).join(
        CandidateCommitteeLink,
        CandidateHistory.candidate_key == CandidateCommitteeLink.candidate_key,
    ).join(
        CommitteeHistory,
        CandidateCommitteeLink.committee_key == CommitteeHistory.committee_key,
    ).join(
        aggregate_model,
        CommitteeHistory.committee_id == aggregate_model.committee_id,
    ).filter(
        CandidateHistory.candidate_id.in_(kwargs['candidate_id']),
        CandidateHistory.two_year_period.in_(kwargs['cycle']),
        CommitteeHistory.cycle.in_(kwargs['cycle']),
        CommitteeHistory.designation.in_(['P', 'A']),
        aggregate_model.cycle.in_(kwargs['cycle']),
    ).group_by(
        CandidateHistory.candidate_id,
        aggregate_model.cycle,
        *group_columns
    )


class ScheduleABySizeCandidate(Resource):

    @args.register_kwargs(args.paging)
    @args.register_kwargs(args.make_sort_args())
    @args.register_kwargs(args.schedule_a_candidate_aggregate)
    @schemas.marshal_with(schemas.ScheduleABySizeCandidatePageSchema())
    def get(self, **kwargs):
        group_columns = [ScheduleABySize.size]
        query = candidate_aggregate(ScheduleABySize, group_columns, group_columns, kwargs)
        return utils.fetch_page(query, kwargs)


class ScheduleAByStateCandidate(Resource):

    @args.register_kwargs(args.paging)
    @args.register_kwargs(args.make_sort_args())
    @args.register_kwargs(args.schedule_a_candidate_aggregate)
    @schemas.marshal_with(schemas.ScheduleAByStateCandidatePageSchema())
    def get(self, **kwargs):
        query = candidate_aggregate(
            ScheduleAByState,
            [
                ScheduleAByState.state,
                sa.func.max(ScheduleAByState.state_full).label('state_full'),
            ],
            [ScheduleAByState.state],
            kwargs,
        )
        return utils.fetch_page(query, kwargs)
