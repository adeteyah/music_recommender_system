def precision_at_k(relevances, k):
    """Calculate precision at rank k."""
    relevant_items = relevances[:k]
    return sum(relevant_items) / k


def average_precision(relevances):
    """Calculate Average Precision (AP) for a single user."""
    precisions = []
    num_relevant = 0

    for i, relevance in enumerate(relevances):
        if relevance == 1:
            num_relevant += 1
            precisions.append(precision_at_k(relevances, i + 1))

    if num_relevant == 0:
        return 0.0

    return sum(precisions) / num_relevant


def mean_average_precision(recommendations, relevances):
    """Calculate Mean Average Precision (MAP) for all users."""
    ap_scores = []

    for relevance in relevances:
        ap_scores.append(average_precision(relevance))

    return sum(ap_scores) / len(ap_scores)

# Example usage:
# Assuming 3 users, with 5 recommendations each
# Relevance lists: 1 means relevant, 0 means not relevant


relevances = [
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
        1, 1, 0, 0, 1, 1, 1, 1, 1, 1]  # CF hani2002.hr@gmail.com
    # CBF hani2002.hr@gmail.com
    # CF_CBF hani2002.hr@gmail.com
    # CBF_CBF hani2002.hr@gmail.com

    # CF flandimr21@gmail.com
    # CBF flandimr21@gmail.com
    # CF_CBF flandimr21@gmail.com
    # CBF_CBF flandimr21@gmail.com

    # CF ghazimgz4@gmail.com
    # CBF ghazimgz4@gmail.com
    # CF_CBF ghazimgz4@gmail.com
    # CBF_CBF ghazimgz4@gmail.com

    # CF annisaadd05@gmail.com
    # CBF annisaadd05@gmail.com
    # CF_CBF annisaadd05@gmail.com
    # CBF_CBF annisaadd05@gmail.com

    # CF riodwipratama08@gmail.com
    # CBF riodwipratama08@gmail.com
    # CF_CBF riodwipratama08@gmail.com
    # CBF_CBF riodwipratama08@gmail.com

    # CF fkadhafi67@gmail.com
    # CBF fkadhafi67@gmail.com
    # CF_CBF fkadhafi67@gmail.com
    # CBF_CBF fkadhafi67@gmail.com

    # CF restumuhammadalfaridzi@gmail.com
    # CBF restumuhammadalfaridzi@gmail.com
    # CF_CBF restumuhammadalfaridzi@gmail.com
    # CBF_CBF restumuhammadalfaridzi@gmail.com

    # CF lutfishidi23@gmail.com
    # CBF lutfishidi23@gmail.com
    # CF_CBF lutfishidi23@gmail.com
    # CBF_CBF lutfishidi23@gmail.com

    # CF dandidaro@gmail.com
    # CBF dandidaro@gmail.com
    # CF_CBF dandidaro@gmail.com
    # CBF_CBF dandidaro@gmail.com

    # CF vini.puteri02@gmail.com
    # CBF vini.puteri02@gmail.com
    # CF_CBF vini.puteri02@gmail.com
    # CBF_CBF vini.puteri02@gmail.com

    # CF sandis2703@gmail.com
    # CBF sandis2703@gmail.com
    # CF_CBF sandis2703@gmail.com
    # CBF_CBF sandis2703@gmail.com

    # CF Puteribrilliantfebriyanti@gmail.com
    # CBF Puteribrilliantfebriyanti@gmail.com
    # CF_CBF Puteribrilliantfebriyanti@gmail.com
    # CBF_CBF Puteribrilliantfebriyanti@gmail.com

    # CF daffa.almunawwar@mhs.itenas.ac.id
    # CBF daffa.almunawwar@mhs.itenas.ac.id
    # CF_CBF daffa.almunawwar@mhs.itenas.ac.id
    # CBF_CBF daffa.almunawwar@mhs.itenas.ac.id

    # CF royaljelly300@gmail.com
    # CBF royaljelly300@gmail.com
    # CF_CBF royaljelly300@gmail.com
    # CBF_CBF royaljelly300@gmail.com

    # CF rofiqmeidiansyah18@gmail.com
    # CBF rofiqmeidiansyah18@gmail.com
    # CF_CBF rofiqmeidiansyah18@gmail.com
    # CBF_CBF rofiqmeidiansyah18@gmail.com

    # CF eqirafi@gmail.com
    # CBF eqirafi@gmail.com
    # CF_CBF eqirafi@gmail.com
    # CBF_CBF eqirafi@gmail.com

    # CF riovelio28@gmail.com
    # CBF riovelio28@gmail.com
    # CF_CBF riovelio28@gmail.com
    # CBF_CBF riovelio28@gmail.com

    # CF bintangmahardikashandy@gmail.com
    # CBF bintangmahardikashandy@gmail.com
    # CF_CBF bintangmahardikashandy@gmail.com
    # CBF_CBF bintangmahardikashandy@gmail.com

    # CF asyifamutiaramaulina30@gmail.com
    # CBF asyifamutiaramaulina30@gmail.com
    # CF_CBF asyifamutiaramaulina30@gmail.com
    # CBF_CBF asyifamutiaramaulina30@gmail.com

    # CF addienaf2001@gmail.com
    # CBF addienaf2001@gmail.com
    # CF_CBF addienaf2001@gmail.com
    # CBF_CBF addienaf2001@gmail.com
]


# Calculate MAP
map_score = mean_average_precision(recommendations=None, relevances=relevances)
print(f"Mean Average Precision (MAP): {map_score:.4f}")
