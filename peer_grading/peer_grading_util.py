from django.db.models import Count
from controller.models import SubmissionState, GraderStatus, Grader, Submission
import logging
from metrics import metrics_util
from metrics.timing_functions import initialize_timing

log = logging.getLogger(__name__)

def get_single_peer_grading_item(location, grader_id):
    """
    Gets instructor grading for a given course id.
    Returns one submission id corresponding to the course.
    Input:
        location - problem location.
        grader_id - student id of the peer grader
    Returns:
        found - Boolean indicating whether or not something to grade was found
        sub_id - If found, the id of a submission to grade
    """
    found = False
    sub_id = 0
    to_be_graded = Submission.objects.filter(
        location=location,
        state=SubmissionState.waiting_to_be_graded,
        next_grader_type="PE",
    ).exclude(student_id=int(grader_id))

    #Do some checks to ensure that there are actually items to grade
    if to_be_graded is not None:
        to_be_graded_length = to_be_graded.count()
        if to_be_graded_length > 0:
            #Set the maximum number of records to search through
            submissions_to_grade = (to_be_graded.filter(grader__isnull=True).values("id")[:50])
            submissions_to_grade_count = submissions_to_grade.count()

            if submissions_to_grade_count > 0:
                submission_grader_counts = [0] * submissions_to_grade_count
            elif submissions_to_grade_count == 0:
                submissions_to_grade = (to_be_graded
                                        .filter(grader__status_code=GraderStatus.success, grader__grader_type="PE")
                                        .exclude(grader__grader_id=grader_id)
                                        .annotate(num_graders=Count('grader'))
                                        .values("num_graders", "id")
                                        .order_by("num_graders")[:50]
                    )
                submission_grader_counts = [p['num_graders'] for p in submissions_to_grade]

            submission_ids = [p['id'] for p in submissions_to_grade]


            #Ensure that student hasn't graded this submission before!
            #Also ensures that all submissions are searched through if student has graded the minimum one
            for i in xrange(0, len(submission_ids)):
                minimum_index = submission_grader_counts.index(min(submission_grader_counts))
                grade_item = Submission.objects.get(id=int(submission_ids[minimum_index]))
                previous_graders = [p.grader_id for p in grade_item.get_successful_peer_graders()]
                if grader_id not in previous_graders:
                    grade_item.state = SubmissionState.being_graded
                    grade_item.save()
                    found = True
                    sub_id = grade_item.id

                    #Insert timing initialization code
                    initialize_timing(sub_id)

                    return found, sub_id
                else:
                    if len(submission_ids) > 1:
                        submission_ids.pop(minimum_index)
                        submission_grader_counts.pop(minimum_index)

    return found, sub_id


def is_peer_grading_finished_for_submission(submission_id):
    """
    Checks to see whether there are enough reliable peer evaluations of submission to ensure that grading is done.
    Input:
        submission id
    Output:
        Boolean indicating whether or not there are enough reliable evaluations.
    """
    pass

def peer_grading_submissions_pending_for_location(location):
    """
    Get submissions that are graded by instructor
    """
    subs_graded = Submission.objects.filter(location=location,
        state=SubmissionState.waiting_to_be_graded,
        next_grader_type="PE",
    )

    return subs_graded

def peer_grading_submissions_graded_for_location(location, student_id):
    """
    Get submissions that are graded by instructor
    """
    subs_graded = Grader.objects.filter(location=location,
        status_code=GraderStatus.success,
        grader_id = student_id,
    )

    return subs_graded