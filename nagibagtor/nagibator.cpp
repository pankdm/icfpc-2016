#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <sstream>
#include <algorithm>
#include <map>
#include <queue>
#include <thread>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Gmpq.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Boolean_set_operations_2.h>
#include <CGAL/Line_2.h>
#include <CGAL/Iso_rectangle_2.h>
#include <CGAL/convex_hull_2.h>
#include <CGAL/Polygon_set_2.h>

using namespace std;
using namespace CGAL;

using Kernel = Simple_cartesian<Gmpq>;
using Point2 = Kernel::Point_2;
using Segment2 = Kernel::Segment_2;
using Polygon2 = Polygon_2<Kernel>;
using PolygonWithHoles2 = Polygon_with_holes_2<Kernel>;
using Line2 = Line_2<Kernel>;
using IsoRectangle2 = Kernel::Iso_rectangle_2;
using Transformation2 = Aff_transformation_2<Kernel>;
using PolygonSet2 = Polygon_set_2<Kernel>;

static const Point2 kP1(0, 0);
static const Point2 kP2(0, 1);
static const Point2 kP3(1, 1);
static const Point2 kP4(1, 0);
static const IsoRectangle2 kUnit( Point2(0, 0), Point2(1, 1) );

static bool kSkipSegments = true;

void split(const string &s, char delim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
}

Gmpz readGmpz(const string& s) {
    Gmpz num;
    stringstream ss(s);
    ss >> num;
    return num;
}

Gmpq readGmpq(const string& s) {
    vector<string> parts;
    split(s, '/', parts);
    if (2 == parts.size()) {
        return Gmpq( readGmpz(parts[0]), readGmpz(parts[1]) );
    } else if (1 == parts.size()) {
        return Gmpq( readGmpz(s), 1 );
    }
    throw runtime_error("Panic2!");
}

string readString(istream& in) {
    string s;
    while (s.empty()) {
        in >> s;
    }
    return s;
}

Point2 readPoint(istream& in) {
    string s = readString(in);
    vector<string> parts;
    split(s, ',', parts);
    if (2 != parts.size()) {
        throw runtime_error(string("bad input: '") + s + "'");
    }
    return Point2(readGmpq(parts[0]), readGmpq(parts[1]));
}

vector<Point2> gPoints;

struct Facet {
    Transformation2 transformation;
    Polygon2 polygon;
};

bool doIntersect(const Polygon2& p, const Line2& line) {
    for (auto edge = p.edges_begin(); edge != p.edges_end(); ++edge) {
        if (do_intersect(*edge, line)) {
            return true;
        }
    }
    return false;
}

template<typename T>
T sqr(T x) {
    return x*x;
}

struct Solution {
    vector<Facet> facets;
    map<Point2, int> points;

    PolygonSet2 polygon;

    Solution split(const Line2& line, bool up) const {
        Solution result;
        result.points = points;
        for (const auto& facet: facets) {
            if (doIntersect(facet.polygon, line)) {
                Facet facet1;
                facet1.transformation = facet.transformation;
                Facet facet2;
                Transformation2 reflection( sqr(line.b()) - sqr(line.a()), -2*line.a()*line.b(), -2*line.a()*line.c(),
                                            -2*line.a()*line.b(), sqr(line.a()) - sqr(line.b()), -2*line.b()*line.c(),
                                            sqr(line.a()) + sqr(line.b()) );
                facet2.transformation = reflection*facet.transformation;
                auto inverse = facet.transformation.inverse();
                bool fail = false;
                for (auto edge = facet.polygon.edges_begin(); edge != facet.polygon.edges_end(); ++edge) {
                    const auto len2 = edge->squared_length();
                    const auto len2new = edge->transform(facet2.transformation).squared_length();
                    if (len2 != len2new) {
                        throw runtime_error("bad transform");
                    }

                    if (line.has_on_positive_side(edge->source()) == up) {
                        facet1.polygon.push_back(edge->source());
                    } else {
                        facet2.polygon.push_back(reflection(edge->source()));
                    }
                    auto intersect = intersection(*edge, line);
                    if (intersect) {
                        Point2* p = boost::get<Point2>(&*intersect);
                        if (p) {
                            auto revPoint = inverse(*p);
                            if (!result.points.count(revPoint)) {
                                result.points[revPoint] = result.points.size();
                            }
                            facet1.polygon.push_back(*p);
                            facet2.polygon.push_back(*p);
                        } else {
                            fail = true;
                        }
                    }
                }
                auto normalize = [&](Facet& f) {
                    auto area = f.polygon.area();
                    if (area == 0) {
                        return;
                    }
                    vector<Point2> points(f.polygon.size());
                    for (size_t i = 0; i < f.polygon.size(); ++i) {
                        points[i] = f.polygon[i];
                    }
                    points.erase(unique(points.begin(), points.end()), points.end());
                    if (points.empty()) {
                        return;
                    }
                    if (area < 0) {
                        reverse(points.begin(), points.end());
                    }
                    Polygon2 p;
                    for (const auto& pnt: points) {
                        p.push_back(pnt);
                    }
                    f.polygon = p;
                    result.facets.push_back(f);
                };
                if (!fail) {
                    normalize(facet1);
                    normalize(facet2);
                } else {
                    result.facets.push_back(facet);
                }
            } else {
                result.facets.push_back(facet);
            }
        }

        for (const auto& f: result.facets) {
            result.polygon.join(f.polygon);
        }

        return result;
    }

    string sSolution;

    bool isGood() {
        stringstream ss;
        ss << points.size() << endl;

        auto out = [&](const Gmpq& q) {
            if (1 != q.denominator()) {
                ss << q;
            } else {
                ss << q.numerator();
            }
        };

        vector<Point2> vp(points.size());
        for (const auto& p: points) {
            vp[p.second] = p.first;
        }

        for (const auto& p: vp) {
            out(p.x());
            ss << ",";
            out(p.y());
            ss << endl;
        }
        ss << facets.size() << endl;
        map<Point2, Point2> transform;
        for (const auto& f: facets) {
            ss << f.polygon.size();
            Polygon2 transformed;
            auto inverse = f.transformation.inverse();
            for (auto fp = f.polygon.vertices_begin(); fp != f.polygon.vertices_end(); ++fp) {
                auto inv = inverse(*fp);
                if (0 == points.count(inv)) {
                    cout << "point not found" << endl;
                    return false;
                }
                ss << " " << points[inv];
                transformed.push_back(vp[points[inv]]);
                transform[inv] = *fp;
            }
            ss << endl;
            auto area = transformed.area();
            if (0 == area) {
                cout << "empty facet" << endl;
                return false;
            }
            if (abs(area) != abs(f.polygon.area())) {
                cout << "not congruent" << endl;
                return false;
            }
        }
        for (const auto& p: vp) {
            if (!transform.count(p)) {
                cout << "point not found 2" << endl;
                return false;
            }
            auto transformed = transform[p];
            out(transformed.x());
            ss << ",";
            out(transformed.y());
            ss << endl;
        }
        sSolution = ss.str();
        // cout << sSolution << endl;
        return sSolution.size() < 5000;
    }
};

Gmpq area(const PolygonWithHoles2& p) {
    Gmpq result = abs(p.outer_boundary().area());
    for (auto hole = p.holes_begin(); hole != p.holes_end(); ++hole) {
        result -= abs(hole->area());
    }
    return result;
}

Gmpq area(const PolygonSet2& p) {
    vector<PolygonWithHoles2> ps;
    p.polygons_with_holes(back_inserter(ps));
    Gmpq result = 0;
    for (const auto& ph: ps) {
        result += area(ph);
    }
    return result;
}

struct Silhouette {
    void read(istream& in, string& filename) {
        int nPolygons;
        in >> nPolygons;
        int nPlus = 0;
        int nMinus = 0;
        for (int iPolygon = 0; iPolygon < nPolygons; ++iPolygon) {
            int nPoints;
            in >> nPoints;
            Polygon2 p;
            for (int iPoints = 0; iPoints < nPoints; ++iPoints) {
                auto point = readPoint(in);
                p.push_back(point);
                gPoints.push_back(point);
            }
            if (p.area() < 0) {
                polygon.add_hole(p);
                ++nMinus;
            } else {
                polygon.outer_boundary() = p;
                ++nPlus;
            }
        }
        if (1 != nPlus) {
            throw runtime_error("panic " + filename + " " + to_string(nPlus) + " " + to_string(nMinus));
        }

        if (!kSkipSegments) {
            segmentedPolygons.push_back(polygon);
            int nSegments;
            in >> nSegments;
            for (int iSegment = 0; iSegment < nSegments; ++iSegment) {
                Point2 p1 = readPoint(in);
                Point2 p2 = readPoint(in);

                Segment2 segment1(p1, p2);
                Segment2 segment2(p2, p1);

                Line2 line(p1, p2);

                Gmpq minX = 1000000;
                Gmpq maxX = -1000000;
                Gmpq minY = 1000000;
                Gmpq maxY = -1000000;
                bool skip = false;
                auto boundary = polygon.outer_boundary();
                for (auto s = boundary.edges_begin(); s != boundary.edges_end(); ++s) {
                    if (*s == segment1 || *s == segment2) {
                        skip = true;
                    }
                }
                for (auto v = boundary.vertices_begin(); v != boundary.vertices_end(); ++v) {
                    minX = std::min(minX, v->x());
                    maxX = std::max(maxX, v->x());
                    minY = std::min(minY, v->y());
                    maxY = std::max(maxY, v->y());
                }
                if (skip) {
                    continue;
                }

                IsoRectangle2 bbox(Point2(minX, minY), Point2(maxX, maxY));

                auto unitIntersection = intersection(bbox, line);
                if (!unitIntersection) {
                    continue;
                }
                const Segment2* s = get<Segment2>(&*unitIntersection);
                if (!s) {
                    continue;
                }
                vector<Point2> tp1;
                tp1.push_back(s->source());
                tp1.push_back(s->target());
                vector<Point2> tp2;
                tp2.push_back(s->source());
                tp2.push_back(s->target());

                auto examine = [&](const Point2& p) {
                    if (line.oriented_side(p) != ON_NEGATIVE_SIDE) {
                        tp1.push_back(p);
                    }
                    if (line.oriented_side(p) != ON_POSITIVE_SIDE) {
                        tp2.push_back(p);
                    }
                };

                examine(kP1);
                examine(kP2);
                examine(kP3);
                examine(kP4);

                auto makeUnique = [&](vector<Point2>& p) {
                    sort(p.begin(), p.end());
                    p.erase(unique(p.begin(), p.end()), p.end());
                };

                makeUnique(tp1);
                makeUnique(tp2);

                Polygon2 cp1;
                convex_hull_2(tp1.begin(), tp1.end(), back_inserter(cp1));
                Polygon2 cp2;
                convex_hull_2(tp2.begin(), tp2.end(), back_inserter(cp2));

                vector<PolygonWithHoles2> newPolygons;
                for (const auto& p: segmentedPolygons) {
                    try {
                        if (cp1.area() != 0) {
                            intersection(p, cp1, back_inserter(newPolygons));
                        }
                        if (cp2.area() != 0) {
                            intersection(p, cp2, back_inserter(newPolygons));
                        }
                    } catch (...) {
                        newPolygons.push_back(p);
                    }
                }
                segmentedPolygons.swap(newPolygons);
            }
        }
    }

    double calcResemblance(const Solution& s) {
        try {
            vector<PolygonWithHoles2> join;
            PolygonSet2 sJoined = s.polygon;
            sJoined.join(polygon);
            sJoined.polygons_with_holes(back_inserter(join));

            auto vectorArea = [&](const vector<PolygonWithHoles2>& joined) -> Gmpq {
                Gmpq result;
                for (int i = 0; i < joined.size(); ++i) {
                    result += area(joined[i]);
                }
                return result;
            };

            auto areaJoin = vectorArea(join);
            if (areaJoin == 0) {
                return 0;
            }

            PolygonSet2 sIntersection = s.polygon;
            vector<PolygonWithHoles2> intersect;
            sIntersection.intersection(polygon);
            sIntersection.polygons_with_holes(back_inserter(intersect));

            return to_double(vectorArea(intersect)/areaJoin);
        } catch (...) {
            return 0;
        }
    }

    void updateResemblance(const Solution& s, int& imp) {
        auto resemblance = calcResemblance(s);
        // cout << resemblance << " " << bestResemblance << endl;
        if (resemblance > bestResemblance || (s.points.size() == 4 && resemblance == bestResemblance)) {
            bestResemblance = resemblance;
            bestSolution = s;
            string sScore = "scores/" + to_string(id) + ".out";
            double prevScore = -1;
            {
                ifstream ifScore(sScore);
                if (!!ifScore) {
                    ifScore >> prevScore;
                }
            }
            if (prevScore + 0.00001 <= resemblance) {
                string folder = (resemblance == 1.0) ? "exact/" : "output/";
                ofstream oBest(folder + to_string(id) + ".out");
                oBest << s.sSolution;
                ofstream ofScore(sScore);
                ofScore << std::setprecision(10) << resemblance;
                ++imp;
            }
        }
    }

    PolygonWithHoles2 polygon;
    vector<PolygonWithHoles2> segmentedPolygons;
    Solution bestSolution;
    double bestResemblance{0};
    int id;
};

static const int nTasks = 8000;

int main() {
    srand(time(NULL));

    vector<Silhouette> silhouettes;

    auto read = [&](int iTask) {
        string filename = "/Users/denplusplus/Dropbox (Personal)/icfpc2016/tasks/t" + to_string(iTask) + ".txt";
        if (0 == (iTask % 100)) {
            cout << iTask << " " << filename << endl;
        }
        ifstream fIn(filename);
        if (fIn) {
            Silhouette s;
            s.read(fIn, filename);
            s.id = iTask;
            silhouettes.push_back(s);
            // cout << filename << "\t" << s.polygons.size() << endl;
        }
    };

    // read(5153);

    for (int iTask = 0; iTask < nTasks; ++iTask) {
        read(iTask);
    }

    sort(gPoints.begin(), gPoints.end());
    gPoints.erase(unique(gPoints.begin(), gPoints.end()), gPoints.end());
    cout << "gPoints: " << gPoints.size() << endl;

    queue<Solution> candidates;
    Solution s;
    Polygon2 p;
    p.push_back(kP4);
    p.push_back(kP3);
    p.push_back(kP2);
    p.push_back(kP1);
    s.polygon.insert(p);
    s.points[kP1] = 0;
    s.points[kP2] = 1;
    s.points[kP3] = 2;
    s.points[kP4] = 3;
    s.facets.push_back( Facet() );
    s.facets.back().polygon = p;
    s.facets.back().transformation = Transformation2(IDENTITY);
    s.isGood();

    candidates.push(s);

    auto randomPoint = []() -> Point2 {
        return gPoints[rand() % gPoints.size()];
    };

    double bestCurrent = 0;
    while (true) {
        auto s = candidates.front();
        candidates.pop();
        double current = 0;
        int imp = 0;

        for (size_t iTask = 0; iTask < silhouettes.size(); ++iTask) {
            auto& task = silhouettes[iTask];
            task.updateResemblance(s, imp);
            current += task.bestResemblance;
        }
        /*
        static const size_t nThreads = 8;
        vector<thread> threads;
        for (size_t i = 0; i < nThreads; ++i) {
            threads.push_back( thread([&, i]() {
                Solution sCopy = s;
                for (size_t iTask = i; iTask < silhouettes.size(); iTask += nThreads) {
                    auto& task = silhouettes[iTask];
                    task.updateResemblance(sCopy);
                    current += task.bestResemblance;
                }
            }));
        }

        for (auto& t : threads) {
            t.join();
        }
        */

        cout << "Current: " << current << " best: " << bestCurrent << " len: " << candidates.size() << " imp: " << imp << endl;
        if (current > bestCurrent) {
            bestCurrent = current;
        }

        if (current + 100 < bestCurrent) {
            continue;
        }

        auto trySplit = [&](Solution&& ss) {
            if (area(s.polygon) != area(ss.polygon)) {
                if (ss.isGood()) {
                    candidates.push(ss);
                    // cout << s.sSolution << " area: " << area(s.polygon) << endl;
                }
            }
        };

        for (int i = 0; i < 4; ++i) {
            Line2 line(randomPoint(), randomPoint());
            if (0 != line.a() || 0 != line.b()) {
                trySplit(s.split(line, rand() % 2));
            }
        }
    }

    return 0;
}
