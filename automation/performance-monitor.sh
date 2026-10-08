#!/bin/bash
# automation/performance-monitor.sh - Performance monitoring

echo "⚡ Running performance analysis..."

# Monitor generation speed
if [ -f "planning/performance-metrics.json" ]; then
    last_check=$(grep -o '"timestamp":"[^"]*"' planning/performance-metrics.json | tail -1 | cut -d'"' -f4)
    last_words=$(grep -o '"total_words":[0-9]*' planning/performance-metrics.json | tail -1 | cut -d':' -f2)
else
    last_check=""
    last_words=0
fi

# Current metrics
current_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
current_words=$(find manuscript/chapters -name "*.md" -exec wc -w {} + 2>/dev/null | tail -n 1 | awk '{print $1}' || echo "0")
current_chapters=$(ls manuscript/chapters/chapter-*.md 2>/dev/null | wc -l)

# Calculate generation rate if we have previous data
if [ -n "$last_check" ] && [ "$last_words" -gt 0 ]; then
    words_added=$((current_words - last_words))
    
    # Simple time difference calculation (approximate)
    if [ "$words_added" -gt 0 ]; then
        echo "📈 Performance Update:"
        echo "   Words added since last check: $words_added"
        echo "   Current total: $current_words words"
        echo "   Chapters completed: $current_chapters"
        
        # Performance assessment
        if [ "$words_added" -gt 1000 ]; then
            performance_status="excellent"
            echo "   🚀 Performance: Excellent ($words_added words/session)"
        elif [ "$words_added" -gt 500 ]; then
            performance_status="good"
            echo "   ✅ Performance: Good ($words_added words/session)"
        elif [ "$words_added" -gt 100 ]; then
            performance_status="adequate"
            echo "   ⚠️  Performance: Adequate ($words_added words/session)"
        else
            performance_status="slow"
            echo "   🐌 Performance: Slow ($words_added words/session)"
        fi
    else
        performance_status="stalled"
        echo "   ⚠️  No progress detected since last check"
    fi
else
    performance_status="baseline"
    echo "📊 Establishing performance baseline..."
fi

# Update performance metrics
cat > planning/performance-metrics.json << EOF
{
  "timestamp": "$current_time",
  "total_words": $current_words,
  "total_chapters": $current_chapters,
  "performance_status": "$performance_status",
  "session_start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "💾 Performance metrics updated"