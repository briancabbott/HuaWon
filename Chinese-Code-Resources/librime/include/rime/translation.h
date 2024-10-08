//
// Copyleft RIME Developers
// License: GPLv3
//
// 2011-05-02 Wensong He <snowhws@gmail.com>
//

#ifndef RIME_TRANSLATION_H_
#define RIME_TRANSLATION_H_

#include <list>
#include <string>
#include <vector>
#include <rime/candidate.h>
#include <rime/common.h>

namespace rime {

class Translation {
 public:
  Translation() = default;
  virtual ~Translation() = default;

  // A translation may contain multiple results, looks
  // something like a generator of candidates.
  virtual bool Next() = 0;

  virtual shared_ptr<Candidate> Peek() = 0;

  // should it provide the next candidate (negative value, zero) or
  // should it give up the chance for other translations (positive)?
  virtual int Compare(shared_ptr<Translation> other,
                      const CandidateList& candidates);

  bool exhausted() const { return exhausted_; }

 protected:
  void set_exhausted(bool exhausted) { exhausted_ = exhausted; }

 private:
  bool exhausted_ = false;
};

class UniqueTranslation : public Translation {
 public:
  UniqueTranslation(shared_ptr<Candidate> candidate)
      : candidate_(candidate) {
  }

  bool Next();
  shared_ptr<Candidate> Peek();

 protected:
  shared_ptr<Candidate> candidate_;
};

class FifoTranslation : public Translation {
 public:
  FifoTranslation();

  bool Next();
  shared_ptr<Candidate> Peek();

  void Append(const shared_ptr<Candidate>& candy);

  size_t size() const {
    return candies_.size() - cursor_;
  }

 protected:
  std::vector<shared_ptr<Candidate>> candies_;
  size_t cursor_ = 0;
};

class UnionTranslation : public Translation {
 public:
  UnionTranslation();

  bool Next();
  shared_ptr<Candidate> Peek();

  UnionTranslation& operator+= (shared_ptr<Translation> t);

 protected:
  std::list<shared_ptr<Translation>> translations_;
};

shared_ptr<UnionTranslation> operator+ (shared_ptr<Translation> a,
                                        shared_ptr<Translation> b);

} // namespace rime

#endif  // RIME_TRANSLATION_H_
