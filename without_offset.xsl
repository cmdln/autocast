<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="outline/root/item">
            <xsl:call-template name="item">
                <xsl:with-param name="indent"
                                select="1"/>
            </xsl:call-template>
        </xsl:for-each>
    </xsl:template>
    <xsl:template name="item">
        <xsl:param name="indent"/>
        <xsl:if test="$indent > 1">
            <xsl:value-of select="$indent"/>
        </xsl:if>
        <xsl:for-each select="values/text/p/run">
            <xsl:text>- </xsl:text>
            <xsl:value-of select="lit"/>
            <xsl:text>
</xsl:text>
        </xsl:for-each>
        <xsl:for-each select="children/item">
            <xsl:call-template name="item">
                <xsl:with-param name="indent"
                                select="$indent + 1"/>
            </xsl:call-template>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
