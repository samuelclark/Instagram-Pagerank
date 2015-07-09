from pattern.vector import count as vec_count
import networkx as nx
from pprint import pprint
def tags_from_media(media_result):
    """
        builds a list of all hashtags used in media_result
        - media result = {mid: instagram_media_object}
    """
    all_tags = []
    used_tags = {}
    for mid, media in media_result.iteritems():
        if 'tags' in media:
            taghash = "-".join(media['tags'])
            if taghash not in used_tags:
                used_tags[taghash] = mid
                all_tags.append(media['tags'])

        else:
            print "no tags in mid = {0}".format(mid)
    return all_tags


def run_tag_pagerank(media_result, num_tags=25, min_edge_weight=4):
    """
        gets tags, calculates cooccurence, pagerank, builds netkx graph
        - media result = {mid: instagram_media_object}
        - min_freq = minimum  tag frequency to be included in pRank / graph
        - min_edge_weight = minimim number of times 2 tags occur together to be included

        returns {'tag_info': occurence_map, 'tag_page_rank': tag_page_rankings, 'graph': netkxgraph instance}
    """
    all_tags = tags_from_media(media_result)
    tag_info = tag_cooccurence(all_tags, num_tags)
    tpr, graph = get_tag_page_rank(tag_info, min_edge_weight)
    return {'tag_info': tag_info, 'tag_page_rank': tpr, 'graph': graph}


def build_netkgraph(tag_info, min_weight=2):
    """
        builds a networkx graph with nodes for each tag and edges between linked tags
        - tag_info = {'tag': neighbors}
        - min_weight = min_coccurence value to create an edge between two tags
        returns networkxgraph
    """
    tag_map = tag_info['mapping']
    tag_counts = tag_info['counts']
    graph = nx.Graph()
    existing_edges = []
    all_tags = tag_map.keys()
    for tag, neighbor_dist in tag_map.iteritems():
        graph.add_node(tag, count=tag_counts[tag])
        for t in all_tags:
            tag_key = "_".join([tag, t])
            rev_key = "_".join([t, tag])
            val = neighbor_dist.get(t, 0)
            if t != tag and (tag_key not in existing_edges or rev_key not in existing_edges) != t and val >= min_weight:
                existing_edges.append(tag_key)
                existing_edges.append(rev_key)
                #print "adding edge {0} --> {1} --> {2}".format(tag, t, val)
                graph.add_edge(tag, t, weight=val)
            #else:
                #print "skipping {0} --> {1} --> {2}".format(tag, t, val)
    #pprint(graph.edges())
    return graph


def get_tag_counts(all_tags, num_tags=25):
    tag_counts = {}
    for tags in all_tags:
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    not_top_tags = sorted(tag_counts, key=lambda x: tag_counts[x], reverse=True)[num_tags:]
    print "removing --> ",not_top_tags
    for tag in not_top_tags:
        del tag_counts[tag]
    print "tags ====== ", tag_counts
    return tag_counts


def tag_cooccurence(all_tags, min_count=3):
    """
        creates a mapping of {tag: {neighbor: count}}
        <all_tags> = list of tags
    """
    tag_map = {}
    tag_counts = get_tag_counts(all_tags, min_count)
    for tags in all_tags:
        for tag in list(set(tags)):
            tgcpy = tags[:]
            if tag in tag_counts:
                tgcpy.remove(tag)
                tag_map[tag] = tag_map.get(tag, []) + tgcpy

    for tag, neighbors in tag_map.iteritems():
        tag_map[tag] = vec_count(neighbors)

    return {'counts': tag_counts, 'mapping': tag_map}


def get_tag_page_rank(tag_info, min_edge_weight=3):
    """
        calculates the page rank of each tag in tag_info['mapping']
    """
    tag_graph = build_netkgraph(tag_info, min_edge_weight)
    print "calculating pagerank for {0} tags".format(len(tag_info['counts']))
    page_ranks = nx.pagerank(tag_graph, max_iter=1000)
    return page_ranks, tag_graph


def print_page_rank(tag_page_rank, tag_info):
    """
        sorts and prints tags to nice table
    """
    ranked_tags = sorted(tag_page_rank, key=lambda x: tag_page_rank[x], reverse=True)
    print "Tag | Frequency | Page Rank"
    print "------ | --- | ---:"
    for tag in ranked_tags:
        try:
            print "{0} | {1} | {2}".format(tag, tag_info['counts'][tag], tag_page_rank[tag])
        except UnicodeEncodeError as e:
            print "encoding error... {0}".format(e)
